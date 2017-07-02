from chan_bar import *
from chan_bi import *


def run_chan(file_path, out_dir):
    df = pd.DataFrame.from_csv(file_path)
    bar_generator = BarGenerator()
    bi_generator = BiGenerator()

    for index, row in df.iterrows():
        raw_bar = Bar(index, row.High, row.Close, 0)
        result, new_bar = bar_generator.process_bar(raw_bar)
        if result == 'merge':
            bi_generator.replace_last_bar(new_bar)
        elif result == 'new':
            bi_generator.append_bar(new_bar)
        else:
            pass

    ended_bi = bi_generator.ended_bi
    trend_confirmed_bi = bi_generator.trend_confirmed_bi

    processed_bars = bar_generator.processed_bars
    calc_gravity_and_log_change(processed_bars)

    print(ended_bi)
    print(len(ended_bi))
    print(trend_confirmed_bi)

    lines = []
    for bi in ended_bi[1:]:
        start, end = bi.to_line()
        lines.append(start)
        lines.append(end)

    df2 = bars_to_dataframe(processed_bars)
    df2['gravity'] = (df2.high + df2.low) / 2
    calc_log_change(df2)

    del df2['gravity']

    ticker = os.path.basename(file_path).split('.')[0]
    # df2.to_csv(os.path.join(data_dir, ticker + '_processed.csv'))
    os.chdir(out_dir)
    draw_graph(ticker, df2, lines)