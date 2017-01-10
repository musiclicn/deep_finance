from finsymbols import symbols

from pandas_datareader.data import YahooDailyReader
import numpy as np
import pandas as pd
import datetime
import sys
import os

sys.path.append(os.path.join(os.getcwd(), '..'))


class Ticker:
    _sp500_tickers = []

    @staticmethod
    def get_sp500_tickers():
        if len(Ticker._sp500_tickers) > 0:
            # print len(Ticker._sp500_tickers)
            return Ticker._sp500_tickers
        sp500 = symbols.get_sp500_symbols()
        # print sp500
        Ticker._sp500_tickers = [e['symbol'] for e in sp500]
        # print Ticker._sp500_tickers
        return Ticker._sp500_tickers


def get_sp500_tickers():
    return Ticker.get_sp500_tickers()


def reshape():
    a = np.load(r'/tmp/yahoo_data/training.npy')
    b = a.reshape(1027967, 3, 252, 1)
    np.save(r'/tmp/yahoo_data/training.npy', b)

spy_file_path = '/data/spy.csv'


def download_spy():
    start = datetime.datetime(2004, 1, 1)
    end = datetime.datetime(2014, 1, 1)
    df = YahooDailyReader('SPY', start, end).read()
    df.to_csv(spy_file_path)


def cluster_spy():
    df = pd.read_csv(spy_file_path)


def main():
    cluster_spy()
    # download_spy()
    # tickers = get_sp500_tickers()
    # print tickers

if __name__ == "__main__":
    main()
