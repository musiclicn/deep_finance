from config import *
from stock_symbol import get_sp500_tickers
from graph import draw_graph
from chan_bi import generate_bi, BiGenerator

import datetime
import pandas as pd
import numpy as np


class Bar(object):
    def __init__(self, time, high, low, trend=1):
        self.time = time
        self.high = high
        self.low = low
        self.gravity = 0
        self.gravity_log = 0
        self.trend = trend
        self.cur_trend_days = 1
        self.pre_same_trend_days = 0
        self.pre_opposite_trend_days = 0

    def __str__(self):
        return 'Bar {} High:{:.2f} Low:{:.2f} Trend:{}'.format(
            self.time, self.high, self.low, self.trend)

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
    elif bar2.high <= bar1.high and bar2.low <= bar1.low:
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


def process_bars(raw_bars):
    bars = [bar for bar in raw_bars if not np.isnan(bar.high) and not np.isnan(bar.low)]
    processed_bars = []
    first_bar = bars[0]
    processed_bars.append(Bar(first_bar.time, first_bar.high, first_bar.low, 1))

    for bar in bars[1:]:
        bar1 = processed_bars.pop()
        bar2 = bar
        relationship = determine_bar_relationship(bar1, bar2)
        if relationship in [BarRelationship.LEFT_CONTAINS_RIGHT, BarRelationship.RIGHT_CONTAINS_LEFT]:
            new_bar = merge_bars(bar1, bar2, relationship)
            if len(processed_bars) > 0:
                pre_bar = processed_bars[-1]
                if new_bar.trend == pre_bar.trend:
                    new_bar.cur_trend_days = pre_bar.cur_trend_days + 1
            processed_bars.append(new_bar)
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


class BarGenerator(object):
    def __init__(self):
        self.processed_bars = []

    def process_bar(self, raw_bar):
        if np.isnan(raw_bar.high) or np.isnan(raw_bar.low):
            return 'pass', None

        if len(self.processed_bars) == 0:
            first_bar = raw_bar
            new_bar = Bar(first_bar.time, first_bar.high, first_bar.low, 1)
            self.processed_bars.append(new_bar)
            return 'new', new_bar

        processed_bars = self.processed_bars
        bar1 = processed_bars.pop()
        bar2 = raw_bar
        relationship = determine_bar_relationship(bar1, bar2)
        if relationship in [BarRelationship.LEFT_CONTAINS_RIGHT, BarRelationship.RIGHT_CONTAINS_LEFT]:
            new_bar = merge_bars(bar1, bar2, relationship)
            if len(processed_bars) > 0:
                pre_bar = processed_bars[-1]
                if new_bar.trend == pre_bar.trend:
                    new_bar.cur_trend_days = pre_bar.cur_trend_days + 1
            processed_bars.append(new_bar)
            return 'merge', new_bar
            # set_prev_trend_days(new_bar, processed_bars)
        elif relationship == BarRelationship.UP_TREND:
            processed_bars.append(bar1)
            bar2.trend = 1
            processed_bars.append(bar2)
            if bar1.trend == 1:
                bar2.cur_trend_days = bar1.cur_trend_days + 1
            return 'new', bar2
            # set_prev_trend_days(bar2, processed_bars)
        elif relationship == BarRelationship.DOWN_TREND:
            processed_bars.append(bar1)
            bar2.trend = -1
            processed_bars.append(bar2)
            if bar1.trend == -1:
                bar2.cur_trend_days = bar1.cur_trend_days + 1
            # set_prev_trend_days(bar2, processed_bars)
            return 'new', bar2


def calc_log_change(df):
    df['gravity_log'] = np.log(df.gravity) - np.log(df.gravity.shift(1))
    df['high_log'] = np.log(df.high) - np.log(df.gravity.shift(1))
    df['low_log'] = np.log(df.low) - np.log(df.gravity.shift(1))


def calc_gravity_and_log_change(processed_bars):
    first_bar = processed_bars[0]
    first_bar.gravity = (first_bar.high + first_bar.low) / 2
    pre_gravity = first_bar.gravity
    for bar in processed_bars[1:]:
        bar.gravity = (bar.high + bar.low) / 2
        bar.gravity_log = np.log(bar.gravity / pre_gravity)
        pre_gravity = bar.gravity
