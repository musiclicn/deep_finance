from config import class_5_dir

import numpy as np
import pandas as pd
import os
from util import get_sp500_tickers


def get_quantile():
    tickers = get_sp500_tickers()
    change_per_series = None
    for counter, ticker in enumerate(tickers):
        # print ticker
        if counter > 50:
            break
        path = os.path.join(class_5_dir, ticker + '.csv')
        if not os.path.exists(path):
            continue
        df = pd.DataFrame.from_csv(path)
        if change_per_series is None:
            change_per_series = df['change%']
        else:
            # print 'before size: ', change_per_series.size
            change_per_series = change_per_series.append(df['change%']).reset_index(drop=True)
            # print 'after size: ', change_per_series.size

    percentage = np.arange(0.25, 1, 0.25)
    return change_per_series.dropna().quantile(percentage).tolist()


def label(num, quantile):
    for counter, up_bound in enumerate(quantile):
        if num < up_bound:
            return counter
    return counter + 1


def main():
    quantile_in_10 = get_quantile()
    print quantile_in_10
    print label(0.081, quantile_in_10)
    print label(0.011, quantile_in_10)
    print label(-0.005, quantile_in_10)
    print label(-0.105, quantile_in_10)

if __name__ == "__main__":
    main()