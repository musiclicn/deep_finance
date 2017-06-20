class BiFormationStatus(object):
    Candidate = 0
    TrendConfirmed = 1
    BiConfirmed = 2


class BiFactory(object):
    confirmed_bi = []
    trend_confirmed_bi = []
    candidate_bi = []


class Bi(object):
    def __init__(self, bar):
        self.bars = [bar]
        self.trend = bar.trend
        self.status = BiFormationStatus.Candidate

    def append_bar(self, bar):
        self.bars.append(bar)
        assert bar.trend == self.trend
        if len(self.bars) >= 3:
            self.status == BiFormationStatus.TrendConfirmed
            if len(BiFactory.trend_confirmed_bi) >= 1:
                last_trend_confirmed_bi = BiFactory.trend_confirmed_bi.pop()
                BiFactory.confirmed_bi.append(last_trend_confirmed_bi)
            assert BiFactory.candidate_bi[-1] == self
            BiFactory.candidate_bi.pop()
            BiFactory.confirmed_bi.append(self)

    def merge(self, other_bi):
        assert self.status == BiFormationStatus.TrendConfirmed
        assert other_bi == BiFormationStatus.Candidate
        self.bars = self.bars + other_bi.bars


def generate_chan_bi(bars):
    confirmed_bi = BiFactory.confirmed_bi
    trend_confirmed_bi = BiFactory.trend_confirmed_bi
    candidate_bi = BiFactory.candidate_bi
    first = True
    for bar in bars:
        if first:
            candidate_bi.append(Bi(bar))
            continue

        if len(candidate_bi) >= 1:
            current_bi = candidate_bi[-1]
        else:
            current_bi = trend_confirmed_bi[-1]

        current_bi_status = current_bi.status
        current_bi_trend = current_bi.trend
        if current_bi_status == BiFormationStatus.Candidate:
            if bar.trend == current_bi_trend:
                current_bi.append_bar(bar)
            else:# bi candidate fails because bar trend reverse before its trend confirms
                last_bi = trend_confirmed_bi[-1]
                last_bi.merge(current_bi)
                last_bi.append_bar(bar)
        elif current_bi_status == BiFormationStatus.TrendConfirmed:
            if bar.trend == current_bi_trend:
                current_bi.append_bar(bar)
            else:# a new bi candidate forms when bar trend reverse
                candidate_bi.append(Bi(bar))
