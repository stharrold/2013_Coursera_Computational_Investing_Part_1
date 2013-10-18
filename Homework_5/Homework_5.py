#! /usr/bin/env python
"""
Homework 5
Make Bollinger bands.
"""

import matplotlib
matplotlib.use('Agg')

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

import sys
import csv
import time
import math
import copy
import numpy as np
import pandas as pd
import datetime as dt

def calculate_df_bollinger_band_values(ls_symbols, df_close, i_lookback):
    ldt_timestamps = df_close.index
    df_bollinger_band_values = pd.DataFrame(index=ldt_timestamps, columns=ls_symbols)
    df_rolling_mean = pd.rolling_mean(df_close, i_lookback)
    df_rolling_std = pd.rolling_std(df_close, i_lookback)
    df_bollinger_band_values = (df_close - df_rolling_mean) / df_rolling_std
    return df_bollinger_band_values

def main(ls_symbols, dt_start, dt_end, i_lookback, s_key):

    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    c_dataobj = da.DataAccess('Yahoo')
    # list_name = 'sp5002012'
    # ls_symbols = c_dataobj.get_symbols_from_list(list_name)
    # TODO: Track index separately from composite stocks. Trigger could activate off of index.
    # ls_symbols.append('SPY')
    # ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ls_keys = [s_key]
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    # TODO: Track index separately from composite stocks. Trigger could activate off of index.
    df_close = d_data[s_key].copy()
    for s_sym in ls_symbols:
        df_close[s_sym] = df_close[s_sym].fillna(method='ffill')
        df_close[s_sym] = df_close[s_sym].fillna(method='bfill')
        df_close[s_sym] = df_close[s_sym].fillna(1.0)
    print "Writing df_close.csv."
    df_close.to_csv('df_close.csv')

    print "Calculating Bollinger band values."
    df_bollinger_band_values = calculate_df_bollinger_band_values(ls_symbols=ls_symbols,
                                                                  df_close=df_close,
                                                                  i_lookback=i_lookback)
    print "Writing df_bollinger_band_values."
    df_bollinger_band_values.to_csv('df_bollinger_band_values.csv')

if __name__ == '__main__':
    ls_symbols = ['GOOG', 'AAPL', 'MSFT']
    dt_start = dt.datetime(2010, 01, 01, 16)
    dt_end   = dt.datetime(2010, 12, 31, 16)
    i_lookback = 20
    s_key = 'close'

    print "ls_symbols = ", ls_symbols
    print "dt_start = ", dt_start
    print "dt_end = ", dt_end
    print "i_lookback = ", i_lookback
    print "s_key = ", s_key

    main(ls_symbols=ls_symbols, dt_start=dt_start, dt_end=dt_end, i_lookback=i_lookback, s_key=s_key)
