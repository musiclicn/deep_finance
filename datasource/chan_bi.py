from collections import deque


class BiFormationStatus(object):
    Candidate = 0
    TrendConfirmed = 1
    BiConfirmed = 2


class Bi(object):
    @staticmethod
    def create_bi(bars):
        bi = Bi(bars[0])
        for bar in bars[1:]:
            bi.append_bar(bar)
        bi.status = BiFormationStatus.TrendConfirmed

    def __init__(self, bars, status=BiFormationStatus.TrendConfirmed):
        assert len(bars) > 0
        self.bars = bars
        self.trend = bars[0].trend
        self.status = status

    @property
    def last_bar(self):
        return self.bars[-1]

    def append_bar(self, bar):
        self.bars.append(bar)

    def append_bars(self, bars):
        self.bars.extend(bars)

    def merge(self, other_bi):
        assert self.status == BiFormationStatus.TrendConfirmed
        assert self.trend == other_bi.trend
        self.bars = self.bars + other_bi.bars

    def merge_weak_bi_pair(self, weak_bi_pair):
        first_bi, second_bi = weak_bi_pair
        self.append_bars(first_bi.bars)
        self.append_bars(second_bi.bars)

    def to_line(self):
        start = (self.bars[0].time, self.bars[0].gravity)
        end = (self.bars[-1].time, self.bars[-1].gravity)
        return start, end


class WeakBi(Bi):
    def __init__(self, bars):
        # assert len(bars) > 0
        self.bars = bars
        self.trend = bars[0].trend

    @property
    def strength(self):
        strength = 0
        for bar in self.bars:
            strength += bar.gravity_log
        return strength


class PhantomBi(Bi):
    def __init__(self, trend):
        self.trend = trend
        self.bars = []


def try_find_trend_reversed_bi(bar_queue, pre_bi):
    if len(bar_queue) < 4:
        return False, None
    pre_bi_trend = pre_bi.trend
    if pre_bi_trend == -1:
        if bar_queue[-1].low > pre_bi.last_bar.high and bar_queue[-1].low > pre_bi.bars[-2].high and \
                        bar_queue[-1].trend == 1:
            return True, Bi(list(bar_queue))
    elif pre_bi_trend == 1:
        if bar_queue[-1].high < pre_bi.last_bar.low and bar_queue[-1].high < pre_bi.bars[-2].low and \
                        bar_queue[-1].trend == -1:
            return True, Bi(list(bar_queue))
    return False, None


def calculate_weak_bi_strength(weak_bi_pair):
    first, second = weak_bi_pair
    return first.strength + second.strength


def find_trend_reversed_bi(bar_queue, pre_bi_trend):
    bars_temp = []
    while len(bar_queue) > 0:
        if bar_queue[0].trend != pre_bi_trend:
            bars_temp.append(bar_queue.popleft())
        else:
            assert len(bars_temp) >= 3
            return Bi(bars_temp)
    if len(bars_temp) >= 3:
        return Bi(bars_temp)

'''
def generate_bi(bars):
    ended_bi = []
    trend_confirmed_bi = []
    bar_queue = deque(bars)
    first_bi, second_bi = find_first_and_second_bi(bar_queue)
    trend_confirmed_bi.append(first_bi)
    trend_confirmed_bi.append(second_bi)

    while len(bar_queue) > 0:
        pre_trend_confirmed_bi = trend_confirmed_bi[-1]
        pre_bi_trend = pre_trend_confirmed_bi.trend
        trend_reversed_bi = find_reversed_trend_confirmed_bi(bar_queue, pre_trend_confirmed_bi)
        if trend_reversed_bi is None:
            break
        ended_bi.append(trend_confirmed_bi.pop())
        trend_confirmed_bi.append(trend_reversed_bi)

    return ended_bi, trend_confirmed_bi
'''


class BiGenerator(object):

    def __init__(self):
        self.reverse_candidate_bars = deque()
        self.weak_bi_pairs = []
        self.trend_confirmed_bi = []
        self.ended_bi = []
        self.first_run = True

    @property
    def current_bi(self):
        return self.trend_confirmed_bi[-1]

    @property
    def cur_bi_trend(self):
        return self.current_bi.trend

    def replace_last_bar(self, new_bar):
        if len(self.reverse_candidate_bars) > 0:
            self.reverse_candidate_bars[-1] = new_bar
        elif len(self.weak_bi_pairs) > 0:
            bi1, bi2 = self.weak_bi_pairs[-1]
            bi2.bars[-1] = new_bar
        elif len(self.trend_confirmed_bi) > 0:
            self.trend_confirmed_bi[-1].bars[-1] = new_bar

    def append_bar(self, bar):
        """
        if there is a trend confirmed ( this is always true because of phantom bi trick)
            if bar is reverse trend, append to reverse_candidate_bars,
                if reverse_candidate_bars become a reversed_trend_confirmed bi
                    combine weak_bi into the trend_confirmed_bi
                    move trend_confirmed_bi to ended_bi

            else # bar is same trend
                if reverse_candidate_bars is not empty
                    create weak bi from reverse_candidate_bars
                    append bar into reverse_candidate_bars
        """
        if self.first_run:
            phantom_bi = PhantomBi(-1)
            phantom_bi.bars.append(bar)
            self.trend_confirmed_bi.append(phantom_bi)
            self.first_run = False
            return

        if len(self.trend_confirmed_bi) == 0:
            raise IOError('there is no trend confirmed bi')

        if bar.trend != self.cur_bi_trend:
            self.reverse_candidate_bars.append(bar)
            success, reverse_bi = try_find_trend_reversed_bi(self.reverse_candidate_bars, self.current_bi)
            if success:
                pre_bi = self.trend_confirmed_bi.pop()
                self.ended_bi.append(pre_bi)
                self.trend_confirmed_bi.append(reverse_bi)
                self.reverse_candidate_bars.clear()
        else:
            # trend is same
            if len(self.reverse_candidate_bars) == 0:
                self.trend_confirmed_bi[-1].append_bar(bar)
            elif len(self.reverse_candidate_bars) > 0:
                self.reverse_candidate_bars.append(bar)
                if bar.trend == 1:
                    if bar.high >= self.current_bi.last_bar.high:
                        self.trend_confirmed_bi[-1].append_bars(self.reverse_candidate_bars)
                        self.reverse_candidate_bars.clear()
                elif bar.trend == -1:
                    if bar.low <= self.current_bi.last_bar.high:
                        self.trend_confirmed_bi[-1].append_bars(self.reverse_candidate_bars)
                        self.reverse_candidate_bars.clear()
            else:
                raise NotImplemented('unexpected condition')
