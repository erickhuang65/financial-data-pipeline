import os
import pandas as pd
from dotenv import load_dotenv
from src.connectors import AlphaAdvantage, BigQueryClient
from src.etl_processor import ETLProcessor
from src.web_scrapper import WebScrapper

# ALPHA VANTAGE API setup 
alpha_api_url = os.getenv("ALPHA_API_URL")
alpha_api_key = os.getenv("ALPHA_API_KEY")

# BigQuery API setup
credential = os.getenv("BIG_QUERY_CREDENTIALS")
project_id = os.getenv("PROJECT_ID")

#FMP API setup
fmp_api_url = os.getenv("FMP_API_URL")
fmp_api_key = os.getenv("FMP_API_KEY")

# Load Ticker CSV for ETLProcessor class
ticker_csv = os.getenv("TICKER_CSV")
data = pd.read_csv(ticker_csv)
ticker_list = data['Ticker'].tolist()

if __name__ == "__main__":
    alpha_vantage_client = AlphaAdvantage(alpha_api_url, alpha_api_key)
    bigquery_client = BigQueryClient(credential, project_id)
    etl_processor = ETLProcessor(alpha_vantage_client, bigquery_client)
    etl_processor.extract(ticker_list)