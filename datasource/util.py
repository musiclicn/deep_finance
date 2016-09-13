import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
from finsymbols import symbols

import numpy as np


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


def main():
    tickers = get_sp500_tickers()
    print tickers

if __name__ == "__main__":
    main()
