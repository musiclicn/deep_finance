import platform
import os
import datetime
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
    'macd_data': '2_macd_3_close_up_trend_csv',
    'change_per': '2_change_per_in_10',
    'clustering': '3_clustering'
}


if platform.system() == 'Windows':
    data_dir = directory['windows']
else:
    data_dir = directory['linux']
daily_dir = os.path.join(data_dir, folder['raw_data'])
macd_dir = os.path.join(data_dir, folder['macd_data'])
change_per_dir = os.path.join(data_dir, folder['change_per'])
training_data_dir = os.path.join(data_dir, '3_training')

start = datetime.datetime(2004, 1, 1)
end = datetime.datetime(2014, 1, 1)

quantile_10 = [-0.020701544239449997, -0.011687439994779999, -0.0065986042970069998, -0.0027777731480319997,
               0.00054701923373000002, 0.0039177146655779999, 0.0079060633726499973, 0.013143195457900003,
               0.02228610645944]

quantile_5 = [-0.011687439994779999, -0.0027777731480319997, 0.0039177146655779999, 0.013143195457900003]