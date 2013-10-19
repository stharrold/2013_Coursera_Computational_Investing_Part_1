#! /usr/bin/env python

import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import csv
import QSTK.qstkstudy.EventProfiler as ep

def calculate_df_bollinger(df_close, i_lookback):
    df_bollinger_band_values = pd.DataFrame(index=df_close.index, columns=df_close.columns)
    df_rolling_mean = pd.rolling_mean(df_close, i_lookback)
    df_rolling_std = pd.rolling_std(df_close, i_lookback)
    df_bollinger_band_values = (df_close - df_rolling_mean) / df_rolling_std
    return df_bollinger_band_values

def find_events(ls_symbols, df_bollinger):
    ''' Finding the event dataframe '''
    ts_market = df_bollinger['SPY']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_bollinger)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_bollinger.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_bollinger[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_bollinger[s_sym].ix[ldt_timestamps[i - 1]]
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            f_cutoff = -2.0
            f_market = 1.0
            if f_symprice_today <= f_cutoff and f_symprice_yest >= f_cutoff and f_marketprice_today >= f_market:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events


if __name__ == '__main__':
    i_lookback = 20
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
        d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_close = d_data['close']
    df_bollinger = calculate_df_bollinger(df_close, i_lookback)
    df_events = find_events(ls_symbols, df_bollinger)
    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                 s_filename='MyEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
