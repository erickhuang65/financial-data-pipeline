import pandas as pd
import logging
from typing import Optional

class ETLProcessor:
    def __init__(self, alpha_vantage_client, fmp_client, bigquery_client):
        """
        Initialize ETL Process with AlphaVantage and BigQuery 
        Args:
            AlphaVantage (object)
            FMP (Object)
            BigQuery (object)
        """
        # creates instance of alpha vantange and bigquery
        self.alpha_vantage_client = alpha_vantage_client
        self.fmp_client = fmp_client
        self.bigquery_client = bigquery_client
        self.logger = logging.getLogger(__name__)
        
        # setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging and configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('etl_processor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    # could add error handling when symbol isn't found from the ticker_list
    def advantage_extract(self, ticker_list):
        """Takes ticker as dataframe and process each ticker"""
        self.data = [] # self data is reseted after each extraction is performed
        if not ticker_list:
            self.logger.error(f"Stock ticker csv not found")
        for ticker in ticker_list:
            try:
                self.data.append(self.alpha_vantage_client.get_stock_data(ticker))
                self.logger.info(f"Alpha Advantage data extract complete")
            except ValueError as e:
                self.logger.error(f"Error with Alpha Advantage API request {e}")
            else:
                self.logger.info(f"Alpha Advantage API request complete")
        return self.data

    def fmp_extract(self, ticker_list):
        """Takes ticker as dataframe and process each ticker"""
        self.data = []
        counter = 0 
        if not ticker_list:
            self.logger.error(f"Ticker file not found")
            return None
        for ticker in ticker_list:
            try:
                self.logger.info(f"Extracting ticker symbol: {ticker}")
                result = self.fmp_client.get_yearly_data(ticker)
                if result is None:
                    self.logger.error(f"Data for {ticker} is None")
                    continue
                self.data.append(result)
            except ValueError as e:
                self.logger.error(f"Error with FMP API request {e}")
        return self.data

    def transform(self, extracted_data: Optional[list[dict]] = None):
        """
        Transforms nested FMP data into flat structure for BigQuery
        Args:
            extracted_data: List of ticker data dictionaries, or None to use self.data
        Returns:
            Pandas DataFrame to load to BigQuery
        """
        self.formatted_records = []
        try:
            for stock in extracted_data[0]:
                self.formatted_record = {}
                for key, value in stock.items():
                    self.formatted_record[key] = value
                self.formatted_records.append(self.formatted_record)
            self.df = pd.DataFrame(self.formatted_records)
            return self.df
        except Exception as e:
            self.logger.error(f"Error transforming {stock}")
        return self.formatted_records

    def load(self, data, data_table):
        """
        Loads the data to BigQuery Cloud Storage
        Args:
            data (obj): Pandas DataFrame with stock data
            data_table (str): Table reference from os.get()

        Returns:
            console logs successfully loaded data to BigQuery
        """
        try:
            self.bigquery_client.load_dataframe(data, data_table)
            print(f"Successfully loaded dataframe to BigQuery")
        except Exception as e:
            self.logger.error(f"Error loading dataset to BigQuery {e}")
