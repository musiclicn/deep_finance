from util import get_sp500_tickers
import config

import pandas as pd
import numpy as np
import os

start_row_idx = 33
ignore_tail_row = 5
width = 256


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
            if len(df) < start_row_idx + width:
                continue

            for i in xrange(start_row_idx, len(df) - width - ignore_tail_row):
                sub_df = df.iloc[i: i + width]['macd']
                input = sub_df.reshape((16, 16))
                trend = df.iloc[i + width -1]['trend']
                yield input, trend


def prepare_training_data():
    FOLDER = config.directory['linux']
    reader = TrainingReader(os.path.join(FOLDER, '2_macd_3_close_up_trend_csv'))
    training_data = []
    labels = []
    for training_one, label in reader.get_next():
        # print training_one.shape
        # print training_one
        training_data.append(training_one)
        labels.append(label)

    training_data_array = np.array(training_data)
    shape = training_data_array.shape
    training_data_processed = training_data_array.reshape(shape + (1,))
    labels_array = np.array(labels)
    print "training data", training_data_processed.shape
    print "labels ", labels_array.shape
    np.save(os.path.join(FOLDER, 'training.npy'), training_data_processed)
    np.save(os.path.join(FOLDER, 'labels.npy'), labels_array)
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
