from util import get_sp500_tickers

import os
import sys
import pandas as pd
import numpy as np

start_row_idx = 33
ignore_tail_row = 5
width = 252


class TrainingReader(object):
    def __init__(self, folder):
        self._folder = folder

    def get_next(self):
        # if not os.path.exists(output_dir):
        #     os.makedirs(output_dir)
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
                sub_df = df.iloc[i: i + width][['macd', 'signal', 'histogram']]
                # print sub_df.shape
                sub_matrix = sub_df.as_matrix()
                # print matrix
                target_matrix = sub_matrix.transpose()
                trend = df.iloc[i + width]['trend']
                # print "type(trend)", type(trend)
                yield target_matrix, trend
                # print target_matrix
                # print i, target_matrix.shape
                """
                if result_matrix is not None:
                    # print "concatenate"
                    # print target_matrix.shape
                    result_matrix = np.concatenate((result_matrix, target_matrix), axis=0)
                    # print result_matrix.shape
                else:
                    # print "assign"
                    result_matrix = target_matrix
                yield result_matrix
            sys.exit(0)
            """
            # print result_matrix.shape
            # out_file = os.path.join(output_dir, ticker )
            # np.save(out_file, result_matrix)


def main():
    reader = TrainingReader(r'C:\Users\Cheng\data\2_macd_3_close_up_trend_csv')
    for training_data, target in reader.get_next():
        pass
        # print training_data.shape
        # print target


if __name__ == "__main__":
    main()
