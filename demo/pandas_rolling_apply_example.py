import pandas as pd
import numpy as np
import sys


print pd.__version__


def calc_3_day_trend(series):
    # print s[0], s[1], s[2], s[3]
    # print s[1], s[2]
    # sys.exit(0)
    if series[0]<= series[1] <= series[2]:
        return 1
    return 0


def cacl_3_OHLC(df):
    print type(df)
    print df
    print df.shape
    sys.exit(0)
    return 0

    # print df[0], df[1], df[2]


df = pd.DataFrame.from_csv(r'/tmp/yahoo_data/2_macd_3_close_up_trend_csv/AA.csv')
print type(df)
# print df.shape
# print df.iloc[0,]

# df['new_trend'] = df.apply(lambda s: calc(s['Open'], s+1['Open'] ), axis=1 , args={})

# df['new_trend'] = df['Close'].rolling(center=False, window=3).apply(calc_3_day_trend).shift(-2)
# df['new_trend2'] = df[['Open', 'High', 'Low', 'Close']].rolling(center=False, window=4, win_type='boxcar').apply(cacl_3_OHLC).shift(-3)
df['new_trend2'] = df.rolling( window=4).apply(cacl_3_OHLC).shift(-3)
# col = df.rolling(4,)

df.to_csv(r'/tmp/yahoo_data/2_macd_3_close_up_trend_csv/AA_apply.csv')
# print df