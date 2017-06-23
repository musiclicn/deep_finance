from collections import deque


class BiFormationStatus(object):
    Candidate = 0
    TrendConfirmed = 1
    BiConfirmed = 2


class BiFactory(object):
    confirmed_bi = []
    trend_confirmed_bi = []
    candidate_bi = []


class WeakBi(object):
    def __init__(self, bars):
        assert len(bars) > 0
        self.bars = bars
        self.trend = bars[0].trend

    @property
    def strength(self):
        strength = 0
        for bar in self.bars:
            strength += bar.gravity_log
        return strength


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


def generate_first_bi(bar_queue):
    assert len(bar_queue) > 0
    bar_temp = []
    bar = bar_queue.popleft()
    bar_temp.append(bar)
    while len(bar_queue) > 0:
        bar = bar_queue.popleft()
        prev_bar_trend = bar_temp[-1].trend
        if bar.trend != prev_bar_trend:
            bar_temp = [bar]
        elif len(bar_temp) == 3:
            break
        else:
            bar_temp.append(bar)

    # continue until bar trend reverse
    bi_trend = bar_temp[-1].trend
    while len(bar_queue) > 0:
        bar = bar_queue.popleft()
        if bar.trend != bi_trend:
            bar_queue.appendleft(bar)
            return Bi(bar_temp)
        else:
            bar_temp.append(bar)


def determine_trend_reversed(bar_queue, pre_bi_trend):
    if len(bar_queue) < 3:
        return False
    if bar_queue[0].trend != pre_bi_trend and bar_queue[1].trend == bar_queue[0].trend and bar_queue[2].trend == bar_queue[0].trend:
        return True
    return False


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


def find_weak_bi_pair(bar_queue):
    print('deque size: ', len(bar_queue))
    first_bi_trend = bar_queue[0].trend
    first_bi_bars = []
    second_bi_bars = []
    while len(bar_queue) >= 1:
        if bar_queue[0].trend == first_bi_trend:
            bar = bar_queue.popleft()
            first_bi_bars.append(bar)
        else:
            break
    while len(bar_queue) >= 1:
        if bar_queue[0].trend != first_bi_trend:
            bar = bar_queue.popleft()
            second_bi_bars.append(bar)
        else:
            break
    return WeakBi(first_bi_bars), WeakBi(second_bi_bars)


def find_reversal_bi_and_weak_bi_pairs(bar_queue, pre_bi, weak_bi_pairs):
    is_trend_reversed = determine_trend_reversed(bar_queue, pre_bi.trend)
    if is_trend_reversed:
        return find_trend_reversed_bi(bar_queue, pre_bi.trend)
    else:
        weak_bi_pair = find_weak_bi_pair(bar_queue)
        weak_bi_pairs.append(weak_bi_pair)
        return find_reversal_bi_and_weak_bi_pairs(bar_queue, pre_bi, weak_bi_pairs)


# this needs improvement
def merge_weak_bi_pair(pre_bi, reversed_bi, weak_bi_pair):
    pair_strength = calculate_weak_bi_strength(weak_bi_pair)
    if pair_strength > 0:
        if pre_bi.trend == 1:
            pre_bi.merge_weak_bi_pair(weak_bi_pair)
        else:
            reversed_bi.merge_weak_bi_pair(weak_bi_pair)
    else:
        if pre_bi.trend == -1:
            pre_bi.merge_weak_bi_pair(weak_bi_pair)
        else:
            reversed_bi.merge_weak_bi_pair(weak_bi_pair)


# need fix
def process_weak_bi_pairs(weak_bi_pairs, reversed_bi, pre_bi):
    # merge all to previous bi
    for weak_bi_pair in weak_bi_pairs:
        pre_bi.merge_weak_bi_pair(weak_bi_pair)


def find_reversed_trend_confirmed_bi(bar_queue, pre_trend_confirmed_bi):
    # between current bi and next bi, there is a list of pairs of (opposite trend bars, same trend bars)
    # these pairs need to be merged into either current bi or next bi
    # first find all these pairs - call them weak bi
    # decide where to merge these pairs
    # easiest way is to determine the sum of strength of all these pairs and merge to current bi or next bi depending on trend
    pre_bi_trend = pre_trend_confirmed_bi.trend

    is_trend_reversed = determine_trend_reversed(bar_queue, pre_bi_trend)
    if is_trend_reversed:
        trend_reversed_bi = find_trend_reversed_bi(bar_queue, pre_bi_trend)
        return trend_reversed_bi
    else:
        weak_bi_pairs = []
        try:
            reversed_bi = find_reversal_bi_and_weak_bi_pairs(bar_queue, pre_trend_confirmed_bi, weak_bi_pairs)
            print ('weak bi pairs num: ', len(weak_bi_pairs))
            process_weak_bi_pairs(weak_bi_pairs, reversed_bi, pre_trend_confirmed_bi)
            return reversed_bi
        except IndexError:
            print("finish bar deque")
            return


def generate_bi(bars):
    ended_bi = []
    trend_confirmed_bi = []
    bar_queue = deque(bars)
    first_bi = generate_first_bi(bar_queue)
    trend_confirmed_bi.append(first_bi)

    while len(bar_queue) > 0:
        pre_trend_confirmed_bi = trend_confirmed_bi[-1]
        pre_bi_trend = pre_trend_confirmed_bi.trend
        trend_reversed_bi = find_reversed_trend_confirmed_bi(bar_queue, pre_trend_confirmed_bi)
        if trend_reversed_bi is None:
            break
        ended_bi.append(trend_confirmed_bi.pop())
        trend_confirmed_bi.append(trend_reversed_bi)

    return  ended_bi, trend_confirmed_bi
