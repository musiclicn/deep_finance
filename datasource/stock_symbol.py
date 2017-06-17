from finsymbols import symbols


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
