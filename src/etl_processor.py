import pandas as pd
import logging
from typing import Optional
from datetime import datetime
import time
from typing import Optional, List, Dict

# from src.utils.logger import get_logger
# from src.cache.redis_cache import cached

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

        # Track processing statistics
        self.stats = {}
        
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

    def extract_with_retry(self,
                           extraction_func,
                           max_retries: int = 3,
                           retry_delay: int = 5,
                           **kwargs):
        """
        Execute extraction with retry logic
        Args:
            extraction_func: The function to execute extraction
            max_retries: Maximum number of retry attemps
            retry_delay: Seconds to wait between retries

        Return:
            Extraction result
        """
        for attempt in range(max_retries):
            try:
                result = extraction_func(**kwargs)
                return result
            except Exception as e:
                self.logger.warning(f"Extraction attemp {attempt + 1}/{max_retries} failed: {e}")

                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error("All retry attemps exhausted")
                    raise

    # could add error handling when symbol isn't found from the ticker_list
    # def advantage_extract(self, 
    #                       ticker_list):
    #     """
    #     Takes ticker as dataframe and process each ticker
    #     """
    #     if not ticker_list:
    #         self.logger.error("Ticker list is empty ")
    #         raise ValueError("Ticker list cannot be empty")
    #     self.data = [] # self data is reseted after each extraction is performed
    #     if not ticker_list:
    #         self.logger.error(f"Stock ticker csv not found")
    #     for ticker in ticker_list:
    #         try:
    #             self.data.append(self.alpha_vantage_client.get_stock_data(ticker))
    #             self.logger.info(f"Alpha Advantage data extract complete")
    #         except ValueError as e:
    #             self.logger.error(f"Error with Alpha Advantage API request {e}")
    #         else:
    #             self.logger.info(f"Alpha Advantage API request complete")
    #     return self.data

    def fmp_extract(self, 
                    ticker_list: List[str],
                    data_type: str,
                    use_retry: bool = True):
        """
        Takes ticker as dataframe and process each ticker
        """
        if not ticker_list:
            self.logger.error(f"Ticker file not found")
            raise ValueError("Ticker list cannot be empty")
        
        extracted_data = []
        
        self.logger.info(f"Starting FMP extraction for {len(ticker_list)} tickers")

        for ticker in ticker_list:
            try:
                self.logger.info(f"Extracting {data_type} data for ticker symbol: {ticker}")
                
                # Select appropriate extraction FMP method
                if data_type == 'yearly':
                    if use_retry:
                        data = self.extract_with_retry(
                            self.fmp_client.get_yearly_data,
                            ticker=ticker
                        )
                    else:
                        data = self.fmp_client.get_yearly_data(ticker)
                        print(f"Retry was skipped")
                
                elif data_type == 'historical':
                    if use_retry:
                        data = self.extract_with_retry(
                            self.fmp_client.get_historical_data,
                            ticker=ticker
                        )
                    else:
                        data = self.fmp_client.get_historical_data
                
                else:
                    # should catch more error
                    raise ValueError(f"Unknown data type: {data_type}")
                
                if data is not None:
                    extracted_data.append(data)
                    self.stats['extracted'] += 1
                    self.logger.info(f"Successfully extracted {ticker}")
                else:
                    self.logger.warning(f"No data returned for {ticker}")
                
                # Rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                self.logger.error(f"Failed to extract {ticker}: {e}")
                self.stats['errors'] += 1
                continue
        
        self.logger.info(
            f"FMP extraction complete: "
            f"{len(extracted_data)}/{len(ticker_list)} successful"
        )
        
        return extracted_data

    def transform(self, extracted_data: Optional[list[dict]] = None):
        """
        Args:
            Extracted data from FMP
        Returns:
            Pandas dataframe
        """
        if not extracted_data:
            self.logger.error("No data to transform")
            print("🚫 No data to transform")
        
        try:
            if isinstance(extracted_data[0], list):
                flat_data = extracted_data[0]
            else:
                flat_data = extracted_data

            df = pd.DataFrame(flat_data)

            df['data'] = pd.to_datetime(df['date'])
            df['volume'] = df['volume'].astype('int64')

            self.logger.info(f"Transformed {len(df)} records")
            return df
        except Exception as e:
            self.logger.error(f"Error transforming data: {e}")
            raise

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
