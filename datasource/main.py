from download_stock_daily import download_stock_daily_csv
from chan_bar import *
from intra_day_price import download_30_min

from datetime import datetime
import random
from os import path


def download_sp500_past_2_years():
    start_date = datetime.today() - timedelta(days=365 * 2)
    end_date = datetime.today()
    tickers = get_sp500_tickers()
    download_stock_daily_csv(tickers, test_dir, start_date, end_date)


def generate_request_id(tickers):
    if len(tickers) == 1:
        return tickers[0] + str(random.random())
    elif len(tickers) >= 5:
        return str(abs(hash(str(tickers[:4]))))
    else:
        return str(abs(hash(str(tickers))))


def download_tickers_and_run_analysis(tickers):
    request_id = generate_request_id(tickers)
    start_date = datetime.today() - timedelta(days=365 * 2)
    end_date = datetime.today()

    print("request id: {}".format(request_id))
    request_id_dir = path.join(data_dir, request_id)
    make_sure_folder_exists(request_id_dir)
    input_data_dir = path.join(request_id_dir, 'data')
    make_sure_folder_exists(input_data_dir)
    download_stock_daily_csv(tickers, input_data_dir, start_date, end_date)
    # process_csv(os.path.join(test_dir, 'AAPL.csv'), output_dir)
    graph_out_dir = path.join(request_id_dir, 'graph')
    make_sure_folder_exists(graph_out_dir)
    apply_func_to_folder_files(input_data_dir, graph_out_dir, process_csv)

# download_tickers_and_run_analysis(['WEAT', 'USO', 'UNG'])
# download_tickers_and_run_analysis(['BIDU', 'TWTR', 'S', 'DDD', 'DB', 'QCOM', 'ASHR', 'MCHI', 'CRM', 'KR', 'COST', 'MU', 'UAA', 'CHK', 'UBS', 'VLO', 'GRPN', 'WEAT', 'UNG'])
# download_tickers_and_run_analysis(['TSLA'])

tickers = get_sp500_tickers()

_30_min_dir = path.join(data_dir, get_today(), '30min')
_30_min_input_dir = path.join(_30_min_dir, 'input')
make_sure_folder_exists(_30_min_input_dir)
for ticker in tickers:
    download_30_min(ticker, _30_min_input_dir)

_30_min_graph_dir = path.join(_30_min_dir, 'graph')
make_sure_folder_exists(_30_min_graph_dir)
apply_func_to_folder_files(_30_min_input_dir, _30_min_graph_dir, process_csv)

