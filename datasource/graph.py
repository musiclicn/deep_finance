from config import *


from math import pi

import pandas as pd
import os

from bokeh.plotting import figure, show, output_file


def draw_graph(df):
    # file_path = os.path.join(test_dir, 'AAPL.csv')
    # df = pd.DataFrame.from_csv(file_path, index_col=None)[:20]
    # print df.head()
    df["date"] = pd.to_datetime(df.Date)

    # df['Trend'] = df.rolling(window=1).apply(lambda df: 1 if df.Close > df.Open else -1)
    df['Trend'] = df.Close > df.Open
    print df.head()

    inc = df.Trend == True
    dec = df.Trend == False
    w = 12*60*60*1000 # half day in ms

    print type(inc)
    print inc

    del df['High']
    del df['Low']

    df['High'] = df['Open']
    df['Low'] = df['Close']

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title = "AAPL Candlestick")
    p.xaxis.major_label_orientation = pi/4
    p.grid.grid_line_alpha=0.3

    p.segment(df.date, df.High, df.date, df.Low, color="black")
    p.vbar(df.date[inc], w, df.Open[inc], df.Close[inc], fill_color="#D5E1DD", line_color="black")
    p.vbar(df.date[dec], w, df.Open[dec], df.Close[dec], fill_color="#F2583E", line_color="black")

    output_file("candlestick.html", title="candlestick.py example")

    show(p)