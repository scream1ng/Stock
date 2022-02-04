import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

def scrape_ticker(url, category):
    url_text = requests.get(url).text
    soup = BeautifulSoup(url_text, 'lxml')
    table = soup.find('div', class_='tv-screener__content-pane')
    ticker = table.find_all('a', class_='tv-screener__symbol')
    company = table.find_all('span', class_='tv-screener__description')

    tickers = []
    companies = []

    for i in ticker:
        tickers.append(i.text)

    for i in company:
        companies.append(i.text.replace('\n\t\t\t\t\t\t\t\t', ''))

    # pop non-voting stock
    for i, value in enumerate(tickers):
        if value[-2:] == '.R':
            tickers.pop(i)
            companies.pop(i)

    df = pd.DataFrame({'Ticker' : tickers, 'Company' : companies, 'Sector' : category})
    return df

def create_list(country, save=0):
    file_name = country + '.csv'

    if country == 'AX':
        url = "https://www.tradingview.com/markets/stocks-australia/sectorandindustry-sector/"
    elif country == 'BK':
        url = "https://www.tradingview.com/markets/stocks-thailand/sectorandindustry-sector/"
    elif country == 'Crypto':
        url = "https://www.tradingview.com/markets/cryptocurrencies/prices-all/"

    if country == 'Crypto':
        url_text = requests.get(url).text
        soup = BeautifulSoup(url_text, 'lxml')
        table = soup.find('tbody', class_='tv-data-table__tbody')
        ticker = table.find_all('tr', class_='tv-data-table__row')
        description = table.find_all('a', class_='tv-screener__symbol')

        tickers = []
        descriptions = []

        for i in ticker:
            tickers.append(i['data-symbol'].split(':')[1][:-3])

        for i in description:
            descriptions.append(i.text)

        final_df = pd.DataFrame({'Ticker': tickers, 'Description': descriptions})
    else:
        url_text = requests.get(url).text
        soup = BeautifulSoup(url_text, 'lxml')
        table = soup.find('tbody', class_='tv-data-table__tbody')
        category = table.find_all('a', class_='tv-screener__symbol')

        categories = []
        sector_url = []
        final_df = pd.DataFrame(columns=['Ticker', 'Company', 'Sector'])

        # extract categories and url
        for i in category:
            url = 'https://www.tradingview.com' + i['href']
            categories.append(i.text)
            sector_url.append(url)

        # extract ticker and create df
        for i, value in enumerate(categories):
            df = scrape_ticker(sector_url[i], categories[i])
            final_df = final_df.append(df)

    print(final_df)

    if save:
        final_df.to_csv(file_name, index=False)
        print(f'{file_name} saved')

if __name__ == "__main__":
    country = 'Crypto'
    save = 0

    try:
        create_list(country, save)
    except Exception as e:
        print(e)




