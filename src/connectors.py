import requests
import logging
from ratelimit import limits, RateLimitException, sleep_and_retry
import os
import logging
import pandas as pd
from typing import Optional, Dict, Any, List

class AlphaAdvantage:
    def __init__(self, api_url, api_key):
        """
        Initializes AlphaVantage client with API URL and key.
        Args:
            api_url (str): Alpha Vantage API URL.
            api_key (str): Alpha Vantage API key.
        """
        self.api_url = api_url
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

    @sleep_and_retry
    @limits(calls=5, period=60)
    def get_stock_data(self, symbol):
        """
        Fetches daily stock data for a given symbol from Alpha Vantage.
        Args:
            symbol (str): Stock ticker symbol.

        Returns:
            dict: Stock data from API.
        Raises:
            requests.RequestException: If the API request fails.
            ValueError: If the response contains an error or is invalid.
        """
        data = None
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',  
                'symbol': symbol, 
                'apikey': self.api_key
            }
            res = requests.get(self.api_url, params=params, timeout=15.0) #timeout parameter prevents program from hanging
            data = res.json()
            if 'Error Message' in data:
                self.logger.error(f"{data['Error Message']}")
            #self.logger.info(f"Data from the API {data}")
        except requests.ConnectionError as e:
            self.logger.error(f"Failed to connect: {e}")
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error: {e}, Status: {e.response.status_code}")
        except requests.Timeout as e:
            self.logger.error(f"Request timed out: {e}")
        except requests.RequestException as e:
            self.logger.error(f"Request error: {e}")
        return data

class FMPClient:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

    @sleep_and_retry
    @limits(calls=5, period=60)
    def get_yearly_data(self, symbol):
        """get request for one year of stock timeseries data"""
        url = f"{self.api_url}{symbol}&timeseries=365&apikey={self.api_key}"

        # add a logic to handle 402 error messages
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
        except requests.ConnectionError as e:
            self.logger.error(f"Failed to connect to API for {symbol}: {e}")
            return None
        except requests.Timeout as e:
            self.logger.error(f"Request timed out for {symbol}: {e}")
            return None
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error for {symbol}: {e}, Status code: {e.response.status_code}")
            return None
        except requests.RequestException as e:
            self.logger.error(f"Request exception for {symbol}: {e}")
            return None

        try:
            data = res.json()
            return data
        except ValueError as e:
            self.logger.error(f"Invalid JSON response for {symbol}: {e}")
            self.logger.error(f"Response content: {res.text[:200]}...")
            return None

    @sleep_and_retry
    @limits(calls=5, period=60)
    def get_five_year_data(self, symbol):
        """
        Get request for the past 5 year of stock timeseries data
        """
        
        url = f"{self.api_url}{symbol}&timeseries=1825&apikey={self.api_key}"

        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
        except requests.ConnectionError as e:
            self.logger.error(f"Failed to connect to API for {symbol}: {e}")
            return None
        except requests.Timeout as e:
            self.logger.error(f"Request timed out for {symbol}: {e}")
            return None
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error for {symbol}: {e}, Status code: {e.response.status_code}")
            return None
        except requests.RequestException as e:
            self.logger.error(f"Request exception for {symbol}: {e}")
            return None

        try:
            data = res.json()
            return data
        except ValueError as e:
            self.logger.error(f"Invalid JSON response for {symbol}: {e}")
            self.logger.error(f"Response content: {res.text[:200]}...")
            return None
    
    @sleep_and_retry
    @limits(calls=5, period=60)
    def get_historical_data(self, symbol):
        pass