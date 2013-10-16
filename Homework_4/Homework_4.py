#! /usr/bin/env python
"""
Homework_4.py
Find events, create orders, calculate fund value.
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

def create_df_events(f_cutoff, ls_symbols, df_close):
    """
    Create events dataframe.
    Accepts a list of symbols along with start and end date
    Returns the Event Matrix which is a pandas DataFrame
    Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
    (d1)|nan |nan |True|nan |nan |True|
    (d2)|nan |True|nan |nan |nan |nan |
    (d3)|True|nan |True|nan |True|nan |
    (d4)|nan |True|nan |True|nan |nan |
    ...................................
    ...................................
    Also, d1 = start date
    False negatively confirms the event occurance
    True positively confirms the event occurence
    """
    ldt_timestamps = df_close.index
    df_events = pd.DataFrame(index=ldt_timestamps, columns=ls_symbols)
    # TODO: Vectorize using arith on series
    for s_sym in ls_symbols:
        # TODO: Vectorize using arith on subframes
        for dt_timestamp in ldt_timestamps:
            if dt_timestamp == ldt_timestamps[0]:
                dt_yesterday = dt_timestamp
                f_sym_price_yesterday = df_close[s_sym].ix[dt_yesterday]
                continue
            dt_today = dt_timestamp
            f_sym_price_today = df_close[s_sym].ix[dt_today]
             # TODO: vectorize using where on temp frame
            if f_sym_price_yest >= f_cutoff and f_sym_price_today < f_cutoff:
                df_events[s_sym].ix[dt_today] = True
            else:
                False
            dt_yesterday = dt_today
            f_sym_price_yesterday = f_sym_price_today
    return df_events

def create_df_orders(ls_symbols, df_events):
    """
    Create market orders from events.
    Returns a dataframe.
    """
    # TODO: Could skip creating this order list and save time.
    ldt_timestamps = df_events.index
    ls_columns = ['timestamp', 'symbol', 'action', 'shares']
    df_orders = pd.Dataframe(columns=ls_columns)
    # TODO: Vectorize using arith on subframess
    for i_idx, dt_timestamp in enumerate(ldt_timestamps):
        # TODO: Take symbols from events
        # TODO: Vectorize using arith on series
        for s_sym in ls_symbols:
            # TODO: Use where instead of looping.
            if df_events[sym].ix[dt_timestamp] == True:
                dt_buy_date = dt_timestamp
                df_buy_order = pd.DataFrame([{'timestamp':dt_buy_date,
                                              'symbol':s_sym,
                                              'action':'buy'
                                              'shares':100.}])
                # TODO: Don't add rows to a dataframe, inefficient.
                df_orders = df_orders.append(df_buy_order, ignore_index=True, verify_integrity=True)
                try:
                    dt_sell_date = ldt_timestamps[i_idx+5]
                    df_sell_order = pd.DataFrame([{'timestamp':dt_sell_date,
                                                  'symbol':s_sym,
                                                  'action':'sell'
                                                  'shares':100.}])
                    df_orders = df_orders.append(df_sell_order, ignore_index=True, verify_integrity=True)
                except:
                    print "ldt_timestamps[i_idx+5] not possible for ", dt_buy_date
    df_orders.sort(columns='timestamp', inplace=True)
    df_orders.index=range(len(df_test))[::-1]
    return df_orders

def create_df_positions(f_start_cash, ls_symbols, df_close, df_orders):
    """
    Create a data frame of positions in cash and shares.
    """
    ldt_timestamps = df_close.index
    # TODO: Get symbols from df_close.
    ls_columns = ['cash'] + ls_symbols
    df_positions = pd.DataFrame(0., index=ldt_timestamps, columns=ls_columns)
    # TODO: Vectorize using arith on series.
    for dt_timestamp in ldt_timestamps:
        dt_today = dt_timestamp
        # TODO: Use where on temp data fraem.
        if dt_today == ldt_timestamps[0]:
            df_positions['cash'].ix[dt_today] = f_start_cash
        else:
            df_positions.ix[dt_today] = df_positions.ix[dt_yesterday]
            for df_order in df_orders.iterrows():
                if dt_today == df_order['timestamp']:
                    s_act = df_order['action']
                    s_sym = df_order['symbol']
                    f_shr = df_order['shares']
                    f_pri = df_close[sym].ix[dt_today]
                    if s_act == 'buy':
                        df_positions['cash'].ix[dt_today] -= f_shr * f_pri
                        df_positions[sym].ix[dt_today]    += f_shr
                    elif s_act == 'sell':
                        df_positions['cash'].ix[dt_today] += f_shr * f_pri
                        df_positions[sym].ix[dt_today]    -= f_shr
                    else:
                        print "ERROR: s_act neither buy nor sell."
                        print "s_act = ", s_act
        dt_yesterday = dt_today
    return df_positions

def create_df_values(ls_symbols, df_positions, df_close):
    """
    Create a dataframe of values from cash and share positions.
    """
    ldt_timestamps = df_close.index
    df_values = pd.DataFrame(0., index=ldt_timestamps, columns=['value'])
    # TODO: Vectorize arith on subframes
    for dt_timestamp in ldt_timestamps:
        dt_today = dt_timestamp
        df_values['value'].ix[dt_today] = df_positions['cash'].ix[dt_today]
        # TODO: Get symbols from df_close.
        # TODO: Vectorize using arith on series.
        for s_sym in ls_symbols:
            f_shr = df_positions[sym].ix[dt_today]
            f_pri = df_close[sym].ix[dt_today]
            df_values['value'].ix[dt_today] += f_share * f_pri
    return df_values

def create_lf_performance(na_values):
    """
    Compute performance for 1D numpy array of values.
    Return a list of floats.
    """
    f_total_return = na_values[:-1] / na_values[0]
    na_daily_returns = na_values[1:]/na_values[:-1]
    f_avg_daily_return = np.average(na_daily_returns)
    f_stddev_daily_return = np.std(na_daily_returns)
    f_day_annualized_sharpe_ratio = math.sqrt(252.) * f_avg_daily_return / f_stddev_daily_return
    return [f_total_return,
            f_avg_daily_return,
            f_stddev_daily_return,
            f_day_annualized_sharpe_ratio]

def main():
    """
    Main program.
    """

    print "dt_start = ", dt_start
    print "dt_end = ", dt_end
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    print "Importing data."
    c_dataobj = da.DataAccess('Yahoo')
    list_name = 'sp5002012'
    ls_symbols = c_dataobj.get_symbols_from_list(list_name)
    # TODO: Track index separately from composite stocks. Trigger could activate off of index.
    ls_symbols.append('SPY')
    # ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    s_key = 'close'
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

    print "Creating events."
    df_events = create_df_events(f_cutoff=f_cutoff,
                                 ls_symbols=ls_symbols,
                                 df_close=df_close)
    print "Writing df_events.csv."
    df_events.to_csv('df_events.csv')

    print "Creating orders."
    df_orders = create_df_orders(ls_symbols=ls_symbols,
                                 df_events=df_events)
    print "Writing df_orders.csv."
    df_orders.to_csv('df_orders.csv')

    print "Calculating positions."
    df_positions = create_df_positions(f_start_cash=f_start_cash,
                                       ls_symbols=ls_symbols,
                                       df_close=df_close,
                                       df_orders=df_orders)
    print "Writing df_positions.csv."
    df_positions.to_csv('df_positions.csv')
    
    print "Calculating fund values."
    df_values = create_df_values(ls_symbols=ls_symbols,
                                 df_positions=df_positions
                                 df_close=df_close)
    print "Writing values.csv."
    df_values.to_csv('df_values.csv')
    
    print "Calculating performance."
    na_fund_values = df_values['value'].values
    [f_fund_total_return,
     f_fund_avg_daily_return,
     f_fund_stddev_daily_return,
     f_fund_day_annualized_sharpe_ratio] = create_lf_performance(na_values=na_fund_values)

    na_comp_values = df_close['SPY'].values
    [f_comp_total_return,
     f_comp_avg_daily_return,
     f_comp_stddev_daily_return,
     f_comp_day_annualized_sharpe_ratio] = create_lf_performance(na_values=na_comp_values)

    print "f_fund_day_annualized_sharpe_ratio = ", f_fund_day_annualized_sharpe_ratio
    print "f_comp_day_annualized_sharpe_ratio = ", f_comp_day_annualized_sharpe_ratio

    print "f_fund_total_return = ", f_fund_total_return
    print "f_comp_total_return = ", f_comp_total_return

    print "f_fund_stddev_daily_return = ", f_fund_stddev_daily_return
    print "f_comp_stddev_daily_return = ", f_comp_stddev_daily_return

    print "f_fund_avg_daily_return = ", f_fund_avg_daily_return
    print "f_comp_avg_daily_return = ", f_comp_avg_daily_return

    return
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        f_start_cash = 50000.
        f_cutoff = 5.
        dt_start = dt.datetime(2008, 01, 01)
        dt_end   = dt.datetime(2009, 12, 31)
        main()
    else:
        print "Usage: ./Homework_4.py"

