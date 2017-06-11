from datasource import get_sp500_tickers
from datasource import config

import pandas as pd
import numpy as np
import os

start_row_idx = 33
ignore_tail_row = 5
width = 252


class TrainingReader(object):
    def __init__(self, folder):
        self._folder = folder

    def get_next(self):
        tickers = get_sp500_tickers()
        for ticker in tickers:
            print ticker
            file_name = os.path.join(self._folder, ticker + r'.csv')

            if not os.path.exists(file_name):
                print file_name + "does not exist"
                continue

            df = pd.DataFrame.from_csv(file_name)
            # print df.head()
            result_matrix = None
            if len(df) < start_row_idx + width:
                continue

            for i in xrange(start_row_idx, len(df) - width - ignore_tail_row):
                x = [df.iloc[i]['macd'], df.iloc[i]['signal'], df.iloc[i]['histogram']]
                y = df.iloc[i]['change%']
                # print "type(trend)", type(trend)
                yield x, y

    def get_batch(self, size, batch_len=3):
        data = np.zeros([size, batch_len], dtype=np.float)
        output = np.zeros([size], dtype=np.float)
        for i in range(size):
            x, y = next(self.get_next())
            data[i] = np.array(x)
            output[i] = y

        yield data, output


def main():
    FOLDER = config.directory['linux']
    reader = TrainingReader(os.path.join(FOLDER, '2_macd_3_close_up_trend_csv'))
    for input, output in reader.get_next():
        print input
        print output


if __name__ == "__main__":
    main()