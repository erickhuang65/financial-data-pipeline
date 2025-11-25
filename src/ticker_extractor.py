import requests
import pandas as pd
from bs4 import BeautifulSoup

# set up required variables to scrap
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
target_file = 's&p500_ticker.csv'
csv_path = '../../notebooks/s&p500_ticker.csv'
dataframe = pd.DataFrame(columns=[])

# load the webpage for webscrapping
response = requests.get(url).text

# create beautifulsoup object
soup = BeautifulSoup(response, 'html.parser')
data = soup.find_all('tbody')
rows = data[0].find_all('tr')

# loop over the object
count = len(rows)

for row in rows:
    col = row.find_all('td')
    if len(col) != 0:
        data_dict = {'Ticker': col[0].contents[0]}
        df1 = pd.DataFrame(data_dict, index=[0])
        dataframe = pd.concat([dataframe, df1], ignore_index=True)

dataframe.to_csv(target_file)
print("Datascraped and CSV genereated")
