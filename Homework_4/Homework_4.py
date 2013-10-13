#! /usr/bin/env python
"""
Homework 4, Parts 1-3
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

    cash_initial = 50000
    print "cash_initial = ", cash_initial

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
    orders = pd.DataFrame(columns=['timestamp', 'symbol', 'action', 'shares'])
    for sym in ls_symbols:
        for its, ts_today in enumerate(ldt_timestamps):
            ts_todayp5 = ldt_timestamps[its+5]
            if df_events[sym].ix[ts_today] == 1:
                new_buy_order  = pd.DataFrame([dict(timestamp=ts_today, symbol=sym, action='buy', shares=100), ])
                orders = orders.append(new_buy_order, ignore_index=True)
                new_sell_order = pd.DataFrame([dict(timestamp=ts_todayp5, symbol=sym, action='sell', shares=100), ])
                orders = orders.append(new_sell_order, ignore_index=True)
    orders.to_csv('orders.csv')

    # Create data frame for positions.
    positions = pd.DataFrame(0., index = ldt_timestamps, columns = ['cash'] + ls_symbols)

    # Update positions one day at a time.
    # TODO: don't use loops
    for its, ts_today in enumerate(ldt_timestamps):
        if its == 0:
            positions['cash'].ix[ts_today] = cash_initial
        else:
            ts_yesterday = ldt_timestamps[its-1]
            positions.ix[ts_today] = positions.ix[ts_yesterday]
        for iord, order in orders.iterrows():
            ts_order = order['timestamp']
            if ts_today == ts_order:
                act = order['action']
                sym = order['symbol']
                shr = order['shares']
                pri = d_data['actual_close'][sym].ix[ts_today]
                # TODO: positions.ix[ts_today, [sym]] causes TypeError. Why?
                if act == 'buy':
                    positions['cash'].ix[ts_today] -= shr*pri
                    positions[sym].ix[ts_today]    += shr
                elif act == 'sell':
                    positions['cash'].ix[ts_today] += shr*pri
                    positions[sym].ix[ts_today]    -= shr
                else:
                    print "ERROR: act neither buy nor sell."
                    print "act = ", act
    positions.to_csv('positions.csv')

    # Write values from positions.
    values = pd.DataFrame(0., index = ldt_timestamps, columns = ['value'])
    for its, ts_today in enumerate(ldt_timestamps):
        values['value'].ix[ts_today] = positions['cash'].ix[ts_today]
        # TODO: positions.ix[ts_today, [sym]] causes TypeError. Why?
        for sym in ls_symbols:
            values['value'].ix[ts_today] += positions[sym].ix[ts_today] * d_data['actual_close'][sym].ix[ts_today]
    values.to_csv(values.csv)

    # for fund
    na_price = values['value'].values
    na_normalized_price = na_price / na_price[0]
    na_rets = na_normalized_price.copy()
    tsu.returnize0(na_rets)
    daily_ret_fund = na_rets
    avg_daily_ret_fund = np.average(daily_ret_fund)
    std_daily_ret_fund = np.std(daily_ret_fund)
    sharpe_ratio_fund = tsu.get_sharpe_ratio(rets=daily_ret_fund, risk_free=0.00)
    total_ret_fund = na_normalized_price[-1]
    
    # for comparision symbol
    # TODO: Flatten na_price list of lists.
    na_price = d_data['actual_close']['SPY'].values
    na_normalized_price = na_price / na_price[0]
    na_rets = na_normalized_price.copy()
    tsu.returnize0(na_rets)
    daily_ret_comp = na_rets
    avg_daily_ret_comp = np.average(daily_ret_comp)
    std_daily_ret_comp = np.std(daily_ret_comp)
    sharpe_ratio_comp = tsu.get_sharpe_ratio(rets=daily_ret_comp, risk_free=0.00)
    total_ret_comp = na_normalized_price[-1]

    print "sharpe_ratio_fund = ", sharpe_ratio_fund
    print "sharpe_ratio_comp = ", sharpe_ratio_comp

    print "total_ret_fund = ", total_ret_fund
    print "total_ret_comp = ", total_ret_comp

    print "std_daily_ret_fund = ", std_daily_ret_fund
    print "std_daily_ret_comp = ", std_daily_ret_comp

    print "avg_daily_ret_fund = ", avg_daily_ret_fund
    print "avg_daily_ret_comp = ", avg_daily_ret_comp

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
