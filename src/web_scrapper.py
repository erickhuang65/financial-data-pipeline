import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging

class WebScrapper:
    def __init__(self, url, target_file, file_path):
        """
        Initialize WebScrapper class to scrap websites
        Args:
            url (str): website url
            target_file (str): csv file to store the data
            file_path (str): path to the csv file
        """
        self.url = url
        self.target_file = target_file
        self.file_path = file_path
        self.df = pd.DataFrame(columns=["Ticker"])
        self.logger = logging.getLogger(__name__)
    
    def _scrap_table(self):
        """
        load the website for to scrap the table
        returns a data in a csv format
        """
        try:
            response = requests.get(self.res).text
            soup = BeautifulSoup(response, 'html_parser')
            data = soup.find_all('td')
            rows = data[0].find_all('tr')

        except requests.Response as e:
            self.logger.error(f"Error scrapping the website: {e}")
        
        for row in rows:
            col = row.find_all('td')
            if len(col) != 0:
                data_dict = {'Ticker': col[0].contents[0]}
                df1 = pd.DataFrame(data_dict, index=[0])
                dataframe = pd.concat([dataframe, df1], ignore_index=True)
        
        return dataframe.to_csv(self.target_file)
    
    