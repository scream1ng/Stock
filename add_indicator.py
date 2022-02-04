import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import warnings
warnings.simplefilter("ignore")

def get_stock_df_from_csv(ticker):
    try:
        df = pd.read_csv(PATH + ticker + '.csv', index_col=0)
    except FileNotFoundError:
        print("File Doesn't Exist")
    else:
        return df

def add_daily_return_to_df(df):
    df['daily_return'] = (df['Close'] / df['Close'].shift(1)) - 1
    return df

def add_cum_return_to_df(df):
    df['cum_return'] = (1 + df['daily_return']).cumprod()
    return df

def add_bollinger_bands(df):
    df['middle_band'] = df['Close'].rolling(window=20).mean()
    df['upper_band'] = df['middle_band'] + 1.96 * df['Close'].rolling(window=20).std()
    df['lower_band'] = df['middle_band'] - 1.96 * df['Close'].rolling(window=20).std()
    return df

def add_Ichimoku(df):
    hi_val = df['High'].rolling(window=9).max()
    low_val = df['Low'].rolling(window=9).min()
    df['Conversion'] = (hi_val + low_val) / 2

    # Baseline
    hi_val2 = df['High'].rolling(window=26).max()
    low_val2 = df['Low'].rolling(window=26).min()
    df['Baseline'] = (hi_val2 + low_val2) / 2

    # Spans
    df['SpanA'] = ((df['Conversion'] + df['Baseline']) / 2).shift(26)
    hi_val3 = df['High'].rolling(window=52).max()
    low_val3 = df['Low'].rolling(window=52).min()
    df['SpanB'] = ((hi_val3 + low_val3) / 2).shift(26)
    df['Lagging'] = df['Close'].shift(-26)
    return df

def add_cdc(df):
    df['EMA12'] = df['Close'].ewm(span=12, min_periods=11, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, min_periods=25, adjust=False).mean()
    return df

def add_atr(df):
    # Average True Range (atr) | ta.rma(trueRange, length)
    length = 14

    # True Range (tr) | trueRange = na(high[1])? high-low : math.max(math.max(high - low, math.abs(high - close[1])), math.abs(low - close[1]))
    df['TR1'] = df['High'] - df['Low']
    df['TR2'] = (df['High'] - df['Close'].shift(1)).abs()
    df['TR3'] = (df['Low'] - df['Close'].shift(1)).abs()
    df['TR'] = df[['TR1', 'TR2', 'TR3']].max(axis=1)
    df.drop(columns=['TR1', 'TR2', 'TR3'], inplace=True)

    # Simple Moving Average (SMA)
    df['SMA_TR'] = df['TR'].rolling(window=length).mean()

    # # RSI Moving Average (rma)
    alpha = 1 / length
    df['ATR'] = 0
    for i, value in enumerate(df['SMA_TR']):
        if (df['ATR'].iloc[i-1] > 0):
            df['ATR'].iloc[i] = alpha * df['TR'].iloc[i] + (1 - alpha) * df['ATR'].iloc[i-1]
        else:
            df['ATR'].iloc[i] = df['SMA_TR'].iloc[i]
    return df

def add_indicator(PATH):
    files = [i for i in listdir(PATH) if isfile(join(PATH, i))]
    tickers = [os.path.splitext(i)[0] for i in files]
    print(f'Total Stock in {PATH} is {len(tickers)}')

    for (i, ticker) in enumerate(tickers, start=1):
        try:
            print(f'Working on [{i}/{len(tickers)}] : {ticker}')
            new_df = get_stock_df_from_csv(ticker)
            new_df = add_daily_return_to_df(new_df)
            new_df = add_cum_return_to_df(new_df)
            new_df = add_bollinger_bands(new_df)
            new_df = add_Ichimoku(new_df)
            new_df = add_cdc(new_df)
            new_df = add_atr(new_df)
            new_df.to_csv(PATH + ticker + '.csv')
        except Exception as ex:
            print(ex)

if __name__ == "__main__":
    PATH = './Crypto/'
    add_indicator(PATH)
