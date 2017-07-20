from config import *
from stock_symbol import get_sp500_tickers
from graph import draw_graph

import pandas as pd
import numpy as np


class Bar(object):
    def __init__(self, time, high, low, trend=1):
        self.time = time
        self.high = high
        self.low = low
        self.trend = trend
        self.gravity = 0
        self.gravity_log_chg = 0
        self.cur_trend_days = 1
        self.pre_same_trend_days = 0
        self.pre_opposite_trend_days = 0
        self.pre_same_trend_strength = 0
        self.pre_opposite_trend_strength = 0

    def __str__(self):
        return 'Bar High:{0:.2f} Low:{1:.2f} Trend:{2}'.format(self.high, self.low, self.trend)

    def contains(self, other):
        return self.low <= other.low and self.high >= other.high

    def to_dict(self):
        return {
            'time': self.time,
            'high': self.high,
            'low': self.low,
            'trend': self.trend,
            'cur_trend_days': self.cur_trend_days,
            'pre_same_trend_days': self.pre_same_trend_days,
            'pre_opposite_trend_days': self.pre_opposite_trend_days,
        }


def bars_to_dataframe(bars):
    return pd.DataFrame.from_records((bar.to_dict() for bar in bars),
                                     index='time',
                                     columns=['time', 'high', 'low', 'trend', 'cur_trend_days',
                                              'pre_same_trend_days', 'pre_opposite_trend_days'])


class BarRelationship(object):
    LEFT_CONTAINS_RIGHT = 1
    RIGHT_CONTAINS_LEFT = 2
    UP_TREND = 3
    DOWN_TREND = 4


def determine_trend(bar1, bar2):
    if bar2.high >= bar1.high and bar2.low >= bar1.low:
        return BarRelationship.UP_TREND
    elif bar2.high < bar1.high and bar2.low < bar1.low:
        return BarRelationship.DOWN_TREND
    raise Exception('no trend here')


def determine_bar_relationship(bar1, bar2):
    if bar1.contains(bar2):
        return BarRelationship.LEFT_CONTAINS_RIGHT
    elif bar2.contains(bar1):
        return BarRelationship.RIGHT_CONTAINS_LEFT
    return determine_trend(bar1, bar2)


def merge_bars(bar1, bar2, relationship):
    if relationship == BarRelationship.LEFT_CONTAINS_RIGHT:
        if bar1.trend == 1:
            return Bar(bar1.time, bar1.high, bar2.low, bar1.trend)
        elif bar1.trend == -1:
            return Bar(bar1.time, bar2.high, bar1.low, bar1.trend)
    elif relationship == BarRelationship.RIGHT_CONTAINS_LEFT:
        if bar1.trend == 1:
            return Bar(bar1.time, bar2.high, bar1.low, bar1.trend)
        elif bar1.trend == -1:
            return Bar(bar1.time, bar1.high, bar2.low, bar1.trend)
    raise Exception('invalid bars')


def set_prev_trend_days(bar, processed_bars):
    size = len(processed_bars)
    i = size - 1
    while i >= 0:
        old_bar = processed_bars[i]
        i -= 1
        if old_bar.trend != bar.trend:
            bar.pre_opposite_trend_days = old_bar.cur_trend_days
            break
    # continue with previous index
    while i >= 0:
        old_bar = processed_bars[i]
        i -= 1
        if old_bar.trend == bar.trend:
            bar.pre_same_trend_days = old_bar.cur_trend_days
            break


def process_bars(bars):
    processed_bars = []
    first_bar = bars[0]
    processed_bars.append(Bar(first_bar.time, first_bar.high, first_bar.low, 1))

    for bar in bars[1:]:
        bar1 = processed_bars.pop()
        bar2 = bar
        relationship = determine_bar_relationship(bar1, bar2)
        if relationship in [BarRelationship.LEFT_CONTAINS_RIGHT, BarRelationship.RIGHT_CONTAINS_LEFT]:
            new_bar = merge_bars(bar1, bar2, relationship)
            pre_bar = processed_bars[-1]
            processed_bars.append(new_bar)
            if new_bar.trend == pre_bar.trend:
                new_bar.cur_trend_days = pre_bar.cur_trend_days + 1
            set_prev_trend_days(new_bar, processed_bars)

        elif relationship == BarRelationship.UP_TREND:
            processed_bars.append(bar1)
            bar2.trend = 1
            processed_bars.append(bar2)
            if bar1.trend == 1:
                bar2.cur_trend_days = bar1.cur_trend_days + 1
            set_prev_trend_days(bar2, processed_bars)
        elif relationship == BarRelationship.DOWN_TREND:
            processed_bars.append(bar1)
            bar2.trend = -1
            processed_bars.append(bar2)
            if bar1.trend == -1:
                bar2.cur_trend_days = bar1.cur_trend_days + 1
            set_prev_trend_days(bar2, processed_bars)

    return processed_bars


def calc_log_change(df):
    df['gravity_log'] = np.log(df.gravity) - np.log(df.gravity.shift(1))
    df['high_log'] = np.log(df.high) - np.log(df.gravity.shift(1))
    df['low_log'] = np.log(df.low) - np.log(df.gravity.shift(1))


def calc_near_2_trend_strength(df):
    pre_trend = 0
    trend_strengths = [0, 0]
    for index, row in df.iterrows():
        # row.pre_opposite_trend_strength = trend_strengths[-1]
        # row.pre_same_trend_strength = trend_strengths[-2]
        df.set_value(index, 'pre_opposite_trend_strength', trend_strengths[-1])
        df.set_value(index, 'pre_same_trend_strength', trend_strengths[-2])
        if row.trend != pre_trend:
            trend_strengths.append(row.gravity_log)
        else:
            cur_trend_strength = trend_strengths.pop()
            trend_strengths.append(cur_trend_strength + row.gravity_log)


def process_csv(input_dir, out_dir):
    print input_dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    files = os.listdir(input_dir)
    for f in files:
        print f
        file_name = os.path.join(input_dir, f)
        print file_name
        df = pd.DataFrame.from_csv(file_name)
        raw_bars = []
        for index, row in df.iterrows():
            bar = Bar(index, row.High, row.Low, 0)
            raw_bars.append(bar)

        processed_bars = process_bars(raw_bars)
        # print 'processed_bars:', processed_bars
        # print processed_bars[0]
        df2 = bars_to_dataframe(processed_bars)
        df2['gravity'] = (df2.high + df2.low) / 2

        calc_log_change(df2)
        del df2['high']
        del df2['low']
        del df2['gravity']

        calc_near_2_trend_strength(df2)

        # df['label'] = df['gravity_log%'].rolling(center=False, window=1).apply(lable_by_quantile).shift(-1)
        df2.to_csv('/data/out.csv')
        # draw_graph(f, df_result)
        return


def main():
    print 'pandas version:', pd.__version__
    tickers = get_sp500_tickers()
    # download_stock_daily_csv(tickers, test_dir, test_start_date, test_end_date)
    process_csv(test_dir, log_return)

if __name__ == "__main__":
    main()
