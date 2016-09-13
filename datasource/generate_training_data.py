from util import get_sp500_tickers
import config

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


def prepare_training_data():
    FOLDER = config.directory['linux']
    reader = TrainingReader(os.path.join(FOLDER, '2_macd_3_close_up_trend_csv'))
    training_data = []
    lables = []
    for training_one, label in reader.get_next():
        training_data.append(training_one)
        lables.append(label)

    training_data_array = np.array(training_data)
    shape = training_data_array.shape
    training_data_processed = training_data_array.reshape(shape + (1,))
    labels_array = np.array(lables)
    print "training data", training_data_processed.shape
    print "labels ", labels_array.shape
    np.save(os.path.join(FOLDER, 'training.npy'), training_data_processed)
    np.save(os.path.join(FOLDER, 'lables.npy'), labels_array)
    print FOLDER


def main():
    prepare_training_data()
    """
    FOLDER = r'/tmp/yahoo_data/'
    reader = TrainingReader(os.path.join(FOLDER,'2_macd_3_close_up_trend_csv'))
    training_data = []
    lables = []
    for training_one, label in reader.get_next():
        training_data.append(training_one)
        lables.append(label)
        # print training_data.shape
        # print target
    training_data__array = np.array(training_data)
    labels_array = np.array(lables)
    print "training_data__array", training_data__array.shape
    print "labels ", labels_array.shape
    np.save(os.path.join(FOLDER,'training.npy'), training_data__array)
    np.save(os.path.join(FOLDER,'labels.npy'), labels_array)
    """


if __name__ == "__main__":
    main()
