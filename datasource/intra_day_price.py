from config import *

import csv
import datetime
import re
import pandas as pd
import requests
from os import path


def get_google_finance_intraday(ticker, period=60, days=1):
    """
    Retrieve intraday stock data from Google Finance.
    Parameters
    ----------
    ticker : str
        Company ticker symbol.
    period : int
        Interval between stock values in seconds.
    days : int
        Number of days of data to retrieve.
    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the opening price, high price, low price,
        closing price, and volume. The index contains the times associated with
        the retrieved price values.
    """

    uri = 'http://www.google.com/finance/getprices' \
          '?i={period}&p={days}d&f=d,o,h,l,c,v&df=cpct&q={ticker}'.format(ticker=ticker,
                                                                          period=period,
                                                                          days=days)
    page = requests.get(uri)
    reader = csv.reader(page.content.splitlines())
    columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    rows = []
    times = []
    for row in reader:
        if re.match('^[a\d]', row[0]):
            if row[0].startswith('a'):
                start = datetime.datetime.fromtimestamp(int(row[0][1:]))
                times.append(start)
            else:
                times.append(start+datetime.timedelta(seconds=period*int(row[0])))
            rows.append(map(float, row[1:]))
    if len(rows):
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'),
                            columns=columns)
    else:
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'))


def download_google_intraday_to_csv(ticker, out_dir):
    df = get_google_finance_intraday('AAPL', period=60, days=1)
    df.to_csv(path.join(out_dir, ticker + '.csv'))


def download_30_min(ticker, out_dir):
    df = get_google_finance_intraday(ticker, period=30 * 60, days=3 * 30)
    # print(df.shape)
    df.to_csv(path.join(out_dir, ticker + '.csv'))

download_30_min('AAPL', path.join(data_dir, '30min'))
download_30_min('GOOGL', path.join(data_dir, '30min'))
