import pandas as pd
import yfinance as yf
import time
import warnings
warnings.simplefilter("ignore")

def save_csv(folder, ticker, yf_ticker):
    stock = yf.Ticker(yf_ticker)
    try:
        print("Getting Data for :", yf_ticker)
        df = stock.history(period="5y")

        if df.empty:
            pass
        else:
            the_file = folder + ticker +'.csv'
            df.to_csv(the_file)
            print(the_file, "- Saved")
    except:
        print("Couldn't Get Data for :", ticker)

def download_stock_history(country):
    file = country + '.csv'
    PATH = './' + country + '/'

    try:
        tickers = pd.read_csv(file)['Ticker']
    except FileNotFoundError:
        print("File Doesn't Exist")

    number_ticker = 0
    for (i, ticker) in enumerate(tickers, start=1):
        print(f'[File : {i}/{len(tickers)}]')

        if country == 'Crypto':
            yf_ticker = ticker + '-USD'
        else:
            yf_ticker = ticker + '.' + country

        save_csv(PATH, ticker, yf_ticker)
        number_ticker += 1
        # time.sleep(2)

    print(f'Saved {number_ticker} from {len(tickers)}')

if __name__ == "__main__":
    country = 'Crypto'
    download_stock_history(country)




