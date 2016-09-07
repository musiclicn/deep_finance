import pandas as pd
import numpy as np
import random

tmp = pd.DataFrame(np.random.randn(2000, 2)/10000, columns=['A','B'])
tmp['date'] = pd.date_range('2001-01-01',periods=2000)
tmp['ii'] = range(len(tmp))


def gm(ii, df, p):
    x_df = df.iloc[map(int, ii)]
    #print x_df
    v =((((x_df['A']+x_df['B'])+1).cumprod())-1)*p
    #print v
    return v.iloc[-1]

print tmp.head(20)

res = pd.rolling_apply(tmp.ii, 50, lambda x: gm(x, tmp, 5))
print res.tail()