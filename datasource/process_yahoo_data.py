import config
from util import get_sp500_tickers

from pandas_datareader.data import YahooDailyReader
import os
import platform
import datetime
import pandas as pd


if platform.system() == 'Windows':
    data_dir = config.directory['windows']
else:
    data_dir = config.directory['linux']
daily_dir = os.path.join(data_dir, config.folder['raw_data'])
macd_dir = os.path.join(data_dir, config.folder['macd_data'])
training_data_dir = os.path.join(data_dir, '3_training')

start = datetime.datetime(2004, 1, 1)
end = datetime.datetime(2014, 1, 1)


def download_stock_daily_csv():
    tickers = get_sp500_tickers()
    print 'len(tickers)', len(tickers)

    if not os.path.exists(daily_dir):
        os.makedirs(daily_dir)

    for ticker in tickers:
        file_name = os.path.join(daily_dir, ticker + '.csv')
        if os.path.isfile(file_name):
            continue
        try:
            print "Downloading " + ticker
            df = YahooDailyReader(ticker, start, end).read()
            df.to_csv(file_name)
        except IOError as error:
            print error


def calc_macd(df):
    df['12_exma'] = df['Close'].ewm(ignore_na=False, span=12, min_periods=12, adjust=True).mean()
    df['26_exma'] = df['Close'].ewm(ignore_na=False, span=26, min_periods=26, adjust=True).mean()
    df['macd'] = df['12_exma'] - df['26_exma']
    df['signal'] = df['macd'].ewm(ignore_na=False, span=9, min_periods=9, adjust=True).mean()
    df['histogram'] = df['macd'] - df['signal']


def calc_3_day_trend(series):
    if series[0]<= series[1] <= series[2]:
        return 1
    return 0


def calc_next_day_change(series):
    change_per = series[1] /series[0] -1
    if change_per < -0.029:
        return 1
    elif change_per < -0.017:
        return 2
    elif change_per < -0.010:
        return 3
    elif change_per < -0.004:
        return 4
    elif change_per < 0.0006:
        return 5
    elif change_per < 0.006:
        return 6
    elif change_per < 0.013:
        return 7
    elif change_per < 0.02:
        return 8
    elif change_per < 0.03:
        return 9
    return 10


def calculate_macd_and_trend(daily_dir):
    if not os.path.exists(macd_dir):
        os.makedirs(macd_dir)

    tickers = get_sp500_tickers()
    for ticker in tickers:
        file_name = os.path.join(daily_dir, ticker + r'.csv')
        if not os.path.exists(file_name):
            continue

        df = pd.DataFrame.from_csv(file_name)
        calc_macd(df)
        # print datetime.datetime.now().time()
        # df['trend'] = pd.rolling_apply(df['Close'], 3, calc_3_day_trend).shift(-2)
        df['trend'] = df['Close'].rolling(center=False, window=2).apply(calc_next_day_change).shift(-1)
        # df['change_percentage'] = pd.rolling_apply(df['Close'], 2, lambda s: s[1] / s[0] - 1).shift(-1)
        df['change'] = df['Close'].rolling(center=False, window=2).apply(lambda s: s[1] / s[0] - 1).shift(-1)
        # print datetime.datetime.now().time()
        macd_file_name = os.path.join(macd_dir, ticker + r'.csv')
        df.to_csv(macd_file_name)
        print ticker


def download_and_calc_macd_label():
    # download_stock_daily_csv()
    calculate_macd_and_trend(daily_dir)


def main():
    # 1. download SPY 500 stocks historical daily bar
    # download_stock_daily_csv()

    # 2. load csv, calculate MACD and trend
    # this takes around 25 minutes, not so bad
    # calculate_csv_and_trend(daily_dir)

    """
    3. clustering
    :return:
    """
    # generate_training_data(macd_dir, training_data_dir)
    # training_dir = generate_training_and_test_data(macd_and_trend_dir)
    download_and_calc_macd_label()


if __name__ == "__main__":
    main()
