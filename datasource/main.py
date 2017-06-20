from config import *
from stock_symbol import get_sp500_tickers
from download_stock_daily import download_stock_daily_csv

tickers = get_sp500_tickers()
download_stock_daily_csv(tickers, test_dir, test_start_date, test_end_date)
