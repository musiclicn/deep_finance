import config
import pandas as pd
import numpy as np
import os

start_row_idx = 1
ignore_tail_row = 1
width = 128
CLASS_N = 5


class TrainingReader(object):
    def __init__(self, folder, training_percenrage=0.9):
        self._folder = folder
        self._files = os.listdir(folder)
        training_size = int(len(self._files) * training_percenrage)
        self._training_files = self._files[:training_size]
        self._validation_files = self._files[training_size + 1:]

        self.all_x = []
        self.all_y = []
        for x, y in self.traing_data():
            self.all_x.append(x)
            self.all_y.append(y)

        self._batch_cnt = 0

    def traing_data(self):
        return self.get_next(self._training_files)

    def test_data(self):
        return self.get_next(self._validation_files[:10])

    def get_training_data(self):
        all_x = []
        all_y = []
        for x, y in self.traing_data():
            all_x.append(x)
            all_y.append(y)
        return all_x, all_y

    def training_next_batch(self, batch_size):
        batch_index = self._batch_cnt
        self._batch_cnt += 1
        start = batch_index * batch_size
        end = (batch_index + 1) * batch_size
        # start again from beginning, reset index to 0
        if end > len(self.all_y):
            self._batch_cnt = 0
        return np.asarray(self.all_x[ start: end]), np.asarray(self.all_y[start: end])

    def get_test_data(self):
        all_x = []
        all_y = []
        for x, y in self.test_data():
            all_x.append(x)
            all_y.append(y)
        return all_x, all_y

    def get_next(self, files):
        for cnt, file in enumerate(files):
            print cnt, file
            file_name = os.path.join(self._folder, file)

            if not os.path.exists(file_name):
                print file_name + "does not exist"
                continue

            df = pd.DataFrame.from_csv(file_name)
            if len(df) < start_row_idx + width:
                continue

            for i in xrange(start_row_idx, len(df) - width - ignore_tail_row):
                sub_df = df.iloc[i: i + width][['change%', 'open%', 'high%', 'low%', 'cur_label']]
                # sub_df = df.iloc[i: i + width][['change%', 'cur_label']]
                # sub_df = df.iloc[i: i + width]['change%']
                matrix = sub_df.as_matrix()
                input = matrix.reshape((width, 5))
                label = df.iloc[i + width - 1]['label']
                label_5 = np.zeros(CLASS_N)
                label_5[int(label)] = 1
                yield input, label_5


def main():
    reader = TrainingReader(config.change_per_dir)
    for x, y in reader.get_next(reader._files):
        print '*********************'
        print x.shape
        print x
        break

    # x, y  = reader.training_next_batch(64)
    # print type(x), x.shape
    # print type(y), y.shape

    # print x
    # print y
    # i = 0
    # for x, y in reader.get_next():
    #     i = i + 1
    #     if i > 5:
    #         break
    #     print x[-10:]
    #     print "\n\n ******************"
    #     print y
    # reader.next_batch(2)

if __name__ == '__main__':
    main()
