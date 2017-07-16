from chan_bar import *
from chan_bi import *


def dynamic_generate_bi(file_path, out_dir):
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


def old_process_csv(file_path, out_dir):
    df = pd.DataFrame.from_csv(file_path)
    raw_bars = []
    for index, row in df.iterrows():
        bar = Bar(index, row.High, row.Close, 0)
        raw_bars.append(bar)

    processed_bars = process_bars(raw_bars)
    # print 'processed_bars:', processed_bars
    # print processed_bars[0]

    calc_gravity_and_log_change(processed_bars)
    ended_bi, trend_confirmed_bi = generate_bi(processed_bars)
    # bi_generator = BiGenerator()
    # for bar in processed_bars:
    #     bi_generator.append_bar(bar)
    #
    # ended_bi = bi_generator.ended_bi
    # trend_confirmed_bi = bi_generator.trend_confirmed_bi

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
    # del df2['high']
    # del df2['low']
    del df2['gravity']

    # df['label'] = df['gravity_log%'].rolling(center=False, window=1).apply(lable_by_quantile).shift(-1)
    ticker = os.path.basename(file_path).split('.')[0]
    # df2.to_csv(os.path.join(data_dir, ticker + '_processed.csv'))
    os.chdir(out_dir)
    draw_graph(ticker, df2, lines)


def make_sure_folder_exists(target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)


def apply_func_to_folder_files(input_dir, out_dir, func):
    make_sure_folder_exists(out_dir)
    os.chdir(out_dir)
    files = os.listdir(input_dir)
    for f in files:
        print("processing {}".format(f))
        file_path = os.path.join(input_dir, f)
        func(file_path, out_dir)


def get_today():
    today = datetime.datetime.today()
    return today.strftime('%Y%m%d')


def main():
    print 'pandas version:', pd.__version__
    # tickers = get_sp500_tickers()
    # download_stock_daily_csv(tickers, test_dir, test_start_date, test_end_date)
    today = datetime.datetime.today()
    output_dir = os.path.join(data_dir,  today.strftime('%Y%m%d'))
    make_sure_folder_exists(output_dir)
    # process_csv(os.path.join(test_dir, 'AAPL.csv'), output_dir)
    apply_func_to_folder_files(test_dir, output_dir, old_process_csv)

if __name__ == "__main__":
    main()
