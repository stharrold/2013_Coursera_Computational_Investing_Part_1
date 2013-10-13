#! /usr/bin/env python
"""
Homework 4, Part 1
http://wiki.quantsoftware.org/index.php?title=CompInvestI_Homework_4
Outputs file with orders.
Usage:
"""

import matplotlib
matplotlib.use('Agg')

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import sys
import pandas as pd
import numpy as np
import datetime as dt
import copy

def main():

    [orders_file] = sys.argv[1]
    
    dt_start = dt.datetime(2008, 1, 1, 16)
    dt_end = dt.datetime(2009, 12, 31, 16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    print "dt_start = ", dt_start
    print "dt_end = ", dt_end

    dataobj = da.DataAccess('Yahoo')
    list_name = 'sp5002012'
    ls_symbols = dataobj.get_symbols_from_list(list_name)
    ls_symbols.append('SPY')
    # ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ls_keys = ['actual_close']
    print "Fetching data."
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_events(ls_symbols, d_data)

    # # From Homework 2:
    # print "Creating Study"
    # ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
    #             s_filename='MyEventStudy_' + list_name + '_Question3_Attempt2.pdf', b_market_neutral=True, b_errorbars=True,
    #             s_market_sym='SPY')

    # TODO: Don't loop. Use where.
    orders = pd.DataFrame(index=ldt_timestamps, columns=['symbol', 'action', 'shares'])
    for sym in ls_symbols:
        for its, ts_today in enumerate(ldt_timestamps):
            ts_todayp5 = ldt_timestamps[its+5]
            if df_events[sym].ix[ts_today] == 1:
                orders['symbol'].ix[ts_today] = sym
                orders['action'].ix[ts_today] = 'buy'
                orders['shares'].ix[ts_today] = 100
                orders['symbol'].ix[ts_todayp5] = sym
                orders['action'].ix[ts_todayp5] = 'sell'
                orders['shares'].ix[ts_todayp5] = 100
    orders.to_csv(orders_file)

    return

def find_events(ls_symbols, d_data):
    """
    Accepts a list of symbols and stock data frame.
    Returns pandas dataframe of events:
        |IBM |GOOG|XOM |MSFT| GS | JP |
    (d1)|nan |nan |1   |nan |nan |1   |
    (d2)|nan |1   |nan |nan |nan |nan |
    (d3)|1   |nan |1   |nan |1   |nan |
    (d4)|nan |1   |nan |1   |nan |nan |
    ...................................
    ...................................
    Also, d1 = start date
    nan = no information about any event.
    1 = event occured.
    """

    # Finding the event dataframe 
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']

    print "Finding events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index
    
    for s_sym in ls_symbols:
        print "s_sym = ", s_sym
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            # f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            # f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            # f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            # f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1
            # Event is found if actual close of the stock price drops below $5
            if f_symprice_today < 5. and f_symprice_yest >= 5.:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events

if __name__ == '__main__':
    main()
