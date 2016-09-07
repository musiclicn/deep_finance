import os
import pandas.io.data as web
# from finsymbols import symbols
import platform
import datetime
import pandas
import pandas as pd

import config
from util import get_sp500_tickers
from generate_training_data import generate_training_data


if platform.system() == 'Windows':
    data_dir = config.directory['windows']
else:
    data_dir = config.directory['linux']
daily_dir = os.path.join(data_dir, config.folder['raw_data'])
macd_dir = os.path.join(data_dir, config.folder['macd_data'])
training_data_dir = os.path.join(data_dir, '3_training')

# print data_dir
start = datetime.datetime(2004, 1, 1)
end = datetime.datetime(2014, 1, 1)


# def get_sp500_tickers():
#     sp500 = symbols.get_sp500_symbols()
#     tickers = [e['symbol'] for e in sp500]
#     return tickers


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
            df = web.DataReader(ticker, "yahoo", start, end)
            df.to_csv(file_name)
        except IOError as error:
            print error


def calc_macd(df):
    df['12_exma'] = pandas.ewma(df['Close'], span=12, min_periods=12)
    df['26_exma'] = pandas.ewma(df['Close'], span=26, min_periods=26)
    df['macd'] = df['12_exma']  - df['26_exma']
    df['signal'] = pandas.ewma(df['macd'], span=9, min_periods=9)
    df['histogram'] = df['macd'] - df['signal']


def create_trend(close, next_close):
    if next_close > close:
        return 1
    else:
        return 0


# def get_trend(values):
#     # print len(values)
#     for index, close in enumerate(values):
#         if index == len(values) - 1:
#             return 1
#         if values[index] > values[index + 1]:
#             return 0
#
#     return 1

class ChanBar(object):
    def __init__(self, high, low):
        self.high = high
        self.low = low
        # print 'ChanBar', high, low

    @staticmethod
    def contains(bar1, bar2):
        if (bar1.high >= bar2.high and bar1.low <= bar2.low) or (bar2.high >= bar1.high and bar2.low <= bar1.low):
            return True
        return False

    @staticmethod
    def merge(bar1, bar2):
        if (bar1.high >= bar2.high and bar1.low <= bar2.low) or (bar2.high >= bar1.high and bar2.low <= bar1.low):
            return ChanBar(max(bar1.high, bar2.high), max(bar1.low, bar2.low))
        raise TypeError("cannot merge two bars")


def trend(df):
    # print "Function trend"
    assert df.shape[0] == 6
    # print df
    chan_bars = [ChanBar(df.iloc[row_idx][1], df.iloc[row_idx][2]) for row_idx in xrange(1, df.shape[0])]
    # print chan_bars
    merged_bar = []
    for idx in range(1, len(chan_bars)):
        bar = chan_bars[idx]
        pre_bar = chan_bars[idx - 1]
        if len(merged_bar) > 0:
            pre_bar = merged_bar[-1]

        if bar.low < pre_bar.low:
            return df.index[0], 0
        if ChanBar.contains(bar, pre_bar):
            merged_bar.append(ChanBar.merge(bar, pre_bar))

    return df.index[0], 1
    # print bars.iloc[[0]].index
    # return bars.iloc[[0]].index, 1


# next 5 days close up
def close_up_trend(df):
    # print "Function trend"
    assert df.shape[0] == 6
    for row_idx in range(1, df.shape[0]):
        if df.iloc[row_idx][1] < df.iloc[row_idx - 1][1]:
            return df.index[0], 0

    return df.index[0], 1


# next 3 days close up
def close_3_day_up_trend(df):
    # print "Function trend"
    assert df.shape[0] == 4
    for row_idx in range(2, df.shape[0]):
        if df.iloc[row_idx][1] < df.iloc[row_idx - 1][1]:
            return df.index[0], 0

    return df.index[0], 1


def calc_trend(df):
    window = 4
    # df['trend'] = pd.rolling_apply(df['High'], 5, get_trend)
    trend_dict = dict([close_3_day_up_trend(df.iloc[i: i + window]) for i in xrange(len(df) - window)])
    # print trend_dict
    df['trend'] = pd.Series(trend_dict)
    # print "Trend Series"
    # print df.head(20)
    # print df.tail(20).ix[:, ['Close', 'trend']]

    '''
    return
    df['next_close'] = df['Close'].shift(-1)
    df['trend'] = list(map(create_trend, df['Close'], df['next_close']))
    print "Next High shift"
    print df.tail(20).ix[:, ['Close', 'trend']]
    '''


def calculate_csv_and_trend(daily_dir):

    if not os.path.exists(macd_dir):
        os.makedirs(macd_dir)

    tickers = get_sp500_tickers()
    for ticker in tickers:
        file_name = os.path.join(daily_dir, ticker + r'.csv')
        if not os.path.exists(file_name):
            continue

        df = pd.DataFrame.from_csv(file_name)
        # print ticker
        # print df.tail()
        calc_macd(df)
        calc_trend(df)

        # print df.head(20)
        # print "statistics:"
        # print df.groupby('trend').count()

        macd_file_name = os.path.join(macd_dir, ticker + r'.csv')
        df.to_csv(macd_file_name)


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

if __name__ == "__main__":
    main()
