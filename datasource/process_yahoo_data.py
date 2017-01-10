from config import daily_dir, change_per_dir, macd_dir, start, end, quantile_5
from util import get_sp500_tickers
from classification import get_quantile, label

from pandas_datareader.data import YahooDailyReader
import pandas as pd
import os


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


# def calc_next_day_change(series):
#     change_per = series[1] /series[0] -1
#     if change_per < -0.029:
#         return 1
#     elif change_per < -0.017:
#         return 2
#     elif change_per < -0.010:
#         return 3
#     elif change_per < -0.004:
#         return 4
#     elif change_per < 0.0006:
#         return 5
#     elif change_per < 0.006:
#         return 6
#     elif change_per < 0.013:
#         return 7
#     elif change_per < 0.02:
#         return 8
#     elif change_per < 0.03:
#         return 9
#     return 10


def calculate_macd_and_trend(input_dir, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    tickers = get_sp500_tickers()
    for ticker in tickers:
        file_name = os.path.join(input_dir, ticker + r'.csv')
        if not os.path.exists(file_name):
            continue

        df = pd.DataFrame.from_csv(file_name)
        calc_macd(df)
        # print datetime.datetime.now().time()
        # df['trend'] = pd.rolling_apply(df['Close'], 3, calc_3_day_trend).shift(-2)
        # df['trend'] = df['Close'].rolling(center=False, window=2).apply(calc_next_day_change).shift(-1)
        # df['change_percentage'] = pd.rolling_apply(df['Close'], 2, lambda s: s[1] / s[0] - 1).shift(-1)
        df['change'] = df['Close'].rolling(center=False, window=2).apply(lambda s: s[1] / s[0] - 1).shift(-1)
        # print datetime.datetime.now().time()
        macd_file_name = os.path.join(macd_dir, ticker + r'.csv')
        df.to_csv(macd_file_name)
        print ticker


def download_and_calc_macd_label():
    # download_stock_daily_csv()
    calculate_macd_and_trend(daily_dir, macd_dir)


def lable_by_quantile(series):
    return label(series[0], quantile_5)


def calc_change_per(input_dir, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    files = os.listdir(input_dir)
    for f in files:
        print f
        file_name = os.path.join(input_dir, f)
        df = pd.DataFrame.from_csv(file_name)
        df['change%'] = df['Close'].rolling(center=False, window=2).apply(lambda s: s[1] / s[0] - 1)
        df['open%'] = df['Open'] / df['Close'] - 1
        df['high%'] = df['High'] / df['Close'] - 1
        df['low%'] = df['Low'] / df['Close'] - 1
        df['cur_label'] = df['change%'].rolling(center=False, window=1).apply(lable_by_quantile)
        # df['12_exma'] = df['Close'].ewm(ignore_na=False, span=12, min_periods=12, adjust=True).mean()
        # df['26_exma'] = df['Close'].ewm(ignore_na=False, span=26, min_periods=26, adjust=True).mean()
        # df['macd'] = df['12_exma'] - df['26_exma']
        # df['signal'] = df['macd'].ewm(ignore_na=False, span=9, min_periods=9, adjust=True).mean()
        # df['histogram'] = df['macd'] - df['signal']
        df['label'] = df['change%'].rolling(center=False, window=1).apply(lable_by_quantile).shift(-1)
        file_path = os.path.join(out_dir, f)
        df.to_csv(file_path)


def main():
    calc_change_per(daily_dir, change_per_dir)
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
    # download_and_calc_macd_label()


if __name__ == "__main__":
    main()
