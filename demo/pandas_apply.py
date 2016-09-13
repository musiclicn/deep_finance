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


df = pd.DataFrame.from_csv(r'/tmp/yahoo_data/2_macd_3_close_up_trend_csv/MMM.csv')
print type(df)
# print df.shape
# print df.iloc[0,]

# df['new_trend'] = df.apply(lambda s: calc(s['Open'], s+1['Open'] ), axis=1 , args={})

df['new_trend'] = pd.rolling_apply(df['Close'], 3, calc_3_day_trend).shift(-2)
# col = df.rolling(4,)

df.to_csv(r'/tmp/yahoo_data/2_macd_3_close_up_trend_csv/MMM_apply.csv')
# print df