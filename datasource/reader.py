import config
import pandas as pd
import numpy as np
import os

start_row_idx = 1
ignore_tail_row = 1
WIDTH = 128
CLASS_N = 4
FEATURE_N = 6
START_ROW = 22


class TrainingReader(object):
    def __init__(self, folder):
        self._folder = folder
        self._files = os.listdir(folder)
        training_size = len(self._files)
        self._training_files = self._files[:training_size]

        self.all_x = []
        self.all_y = []
        cnt = 0
        for x, y in self.all_data():
            # if cnt > 100:
            #     break
            # print '**********************************'
            # print x[:3]
            # print x[-3:]
            # print y
            # cnt += 1
            self.all_x.append(x)
            self.all_y.append(y)

        self._batch_cnt = 0

    def all_data(self):
        return self.get_next(self._files)

    def training_next_batch(self, batch_size):
        # start again from beginning, reset index to 0
        if (self._batch_cnt + 1) * batch_size > len(self.all_y):
            self._batch_cnt = 0
            print '**********************'
            print 'Reset'

        batch_index = self._batch_cnt
        start = batch_index * batch_size
        end = (batch_index + 1) * batch_size
        self._batch_cnt += 1
        return np.asarray(self.all_x[ start: end]), np.asarray(self.all_y[start: end])

    def get_all_data(self):
        return self.all_x, self.all_y

    def get_next(self, files):
        # pre_time = datetime.datetime.now()
        for cnt, file in enumerate(files):
            print cnt, file
            file_name = os.path.join(self._folder, file)
            # cur_time = datetime.datetime.now()
            # print cur_time - pre_time
            # pre_time = cur_time
            if not os.path.exists(file_name):
                print file_name + "does not exist"
                continue

            df = pd.DataFrame.from_csv(file_name)
            if len(df) < start_row_idx + WIDTH:
                continue

            sub_df = df[['change%', 'open%', 'high%', 'low%', 'std', 'cur_label','label']]
            # print sub_df.head()
            input_matrix = []
            start_index = 1
            row_cnt = 0
            for row in sub_df.itertuples():
                label_index = start_index + FEATURE_N
                # print 'row_cnt:', row_cnt
                row_cnt += 1
                if row_cnt < START_ROW:
                    continue
                if np.isnan(row[start_index]) or np.isnan(row[label_index]):
                    continue
                raw_label = row[label_index]
                one_row = [row[1], row[2], row[3], row[4], row[5], row[6]]
                input_matrix.append(one_row)
                if len(input_matrix) > WIDTH:
                    input_matrix.pop(0)
                if len(input_matrix) == WIDTH:
                    label = np.zeros(CLASS_N)
                    label[int(raw_label)] = 1
                    # print label
                    yield np.array(input_matrix), label


def main():
    reader = TrainingReader(config.class_5_dir)
    for x, y in reader.get_next(reader._files):
        # pass
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
