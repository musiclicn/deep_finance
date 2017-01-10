import numpy as np
import pandas as pd
import os


daily_dir = '/data/yahoo_data/2_change_per_in_10'

for file in ['FOXA.csv']:
    df = pd.DataFrame.from_csv(os.path.join(daily_dir, file))
    percentage= np.arange(0.1, 1, 0.1)
    print percentage
    print type(df['change%'])
    series = df['change%']
    print series.size

    print df['change%'].dropna().quantile(percentage)