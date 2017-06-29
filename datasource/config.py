import platform
import os
from datetime import datetime, timedelta
"""
config = {
    "mysql": {
        "user": "root",
        "pass": "secret",
        "tables": {
            "users": "tb_users"
        }
        # etc
    }
}
"""

directory = {
    'windows': r'C:\Users\Cheng\data',
    'linux': r'/data/yahoo_data'
}

folder = {
    'raw_data': '1_daily_csv',
    'test_data': '1_daily_test',
    'macd_data': '2_macd_3_close_up_trend_csv',
    'class_5': '2_class_5',
    'class_4': '2_class_4',
    'class_4_test': 'class_4_test',
    'class_2': '2_class_2',
    'clustering': '3_clustering'
}


if platform.system() == 'Windows':
    data_dir = directory['windows']
else:
    data_dir = directory['linux']
daily_dir = os.path.join(data_dir, folder['raw_data'])
test_dir = os.path.join(data_dir, folder['test_data'])
graph_dir = os.path.join(data_dir, 'graph')
macd_dir = os.path.join(data_dir, folder['macd_data'])

class_5_dir = os.path.join(data_dir, folder['class_5'])
class_4_dir = os.path.join(data_dir, folder['class_4'])
class_4_test = os.path.join(data_dir, folder['class_4_test'])
class_2_dir = os.path.join(data_dir, folder['class_2'])
training_data_dir = os.path.join(data_dir, '3_training')

log_return = os.path.join(data_dir, 'log_return')

training_start_date = datetime(2004, 1, 1)
training_end_date = datetime(2014, 1, 1)

test_start_date = datetime.today() - timedelta(days=365 * 2)
test_end_date = datetime.today()

quantile_10 = [-0.020701544239449997, -0.011687439994779999, -0.0065986042970069998, -0.0027777731480319997,
               0.00054701923373000002, 0.0039177146655779999, 0.0079060633726499973, 0.013143195457900003,
               0.02228610645944]

quantile_5 = [-0.011687439994779999, -0.0027777731480319997, 0.0039177146655779999, 0.013143195457900003]

quantile_4 = [-0.0089466287702450013, 0.000480261919261, 0.01020912644035]
quantile_2 = [0]