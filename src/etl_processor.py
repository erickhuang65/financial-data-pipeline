import os
from dotenv import load_dotenv
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ALPHA VANTAGE API SETUP
alpha_api_url = os.getenv("ALPHA_API_URL")
alpha_api_key = os.getenv("ALPHA_API_KEY")


class ETLProcessor:
    def __init__(self, config):
        self.config = config
        self.logger = self._setup_logging()

    # config file: should have the csv fil

    def extract(key, api_key, url, table_attribs):
        ''' This function 
        '''
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',  
                'symbol': {key},  
                'apikey': api_key
            }
            res = requests.get(url, params, timeout=15.0) #timeout parameter prevents program from hanging
            print(f"Status Code: {res.status_code}") 
            data = res.json()
            print(f"Data from the API key: {data}")
        except requests.ConnectionError as e:
            print(f"Failed to connect: {e}")
        except requests.HTTPError as e:
            print(f"HTTP error: {e}, Status: {e.response.status_code}")
        except requests.Timeout as e:
            print(f"Request timed out: {e}")
        except requests.RequestException as e:
            print(f"Request erro: {e}")
        finally:
            print("API request attempt completed")
        pass

