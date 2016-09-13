class ChanBar(object):
    def __init__(self, high, low):
        self.high = high
        self.low = low
        # print 'ChanBar', high, low

    @staticmethod
    def contains(bar1, bar2):
        if (bar1.high >= bar2.high and bar1.low <= bar2.low) or (bar2.high >= bar1.high and bar2.low <= bar1.low):
            return True
        return False

    @staticmethod
    def merge(bar1, bar2):
        if (bar1.high >= bar2.high and bar1.low <= bar2.low) or (bar2.high >= bar1.high and bar2.low <= bar1.low):
            return ChanBar(max(bar1.high, bar2.high), max(bar1.low, bar2.low))
        raise TypeError("cannot merge two bars")


def chan_bi_trend(df):
    # print "Function trend"
    assert df.shape[0] == 6
    # print df
    chan_bars = [ChanBar(df.iloc[row_idx][1], df.iloc[row_idx][2]) for row_idx in xrange(1, df.shape[0])]
    # print chan_bars
    merged_bar = []
    for idx in range(1, len(chan_bars)):
        bar = chan_bars[idx]
        pre_bar = chan_bars[idx - 1]
        if len(merged_bar) > 0:
            pre_bar = merged_bar[-1]

        if bar.low < pre_bar.low:
            return df.index[0], 0
        if ChanBar.contains(bar, pre_bar):
            merged_bar.append(ChanBar.merge(bar, pre_bar))

    return df.index[0], 1