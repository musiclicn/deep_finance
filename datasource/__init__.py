from generate_training_data import TrainingReader
from process_yahoo_data import download_and_calc_macd_label
from stock_symbol import get_sp500_tickers
import config

import os
import numpy as np

from reader import TrainingReader
import finsymbols


def prepare_training_data():
    download_and_calc_macd_label()

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