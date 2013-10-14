#! /usr/bin/env python
"""
Homework_4.py
"""

import matplotlib
matplotlib.use('Agg')

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import sys
import time
import math
import pandas as pd
import numpy as np
import datetime as dt
import copy

def find_events(ls_symbols, df_close, f_event_threshold):
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
    # ts_market = df_close['SPY']
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN
    # Time stamps for the event range
    ldt_timestamps = df_close.index
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i-1]]
            # f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            # f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            # f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            # f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1
            # Event is found if actual close of the stock price drops below $5
            if f_symprice_today < f_event_threshold and f_symprice_yest >= f_event_threshold:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
    return df_events

def create_orders(ls_symbols, df_events):
    """
    Create market orders from events.
    """

    # TODO: Take symbols from events.
    # TODO: Don't loop. Use where.
    ls_names = ['timestamp', 'symbol', 'action', 'shares']
    df_orders = pd.DataFrame(columns=ls_names)
    ldt_timestamps = df_events.index
    for sym in ls_symbols:
        for its, ts_today in enumerate(ldt_timestamps):
            if df_events[sym].ix[ts_today] == 1:
                s_new_buy_order = pd.DataFrame([{'timestamp':ts_today, 'symbol':sym, 'action':'buy', 'shares':100}])
                df_orders = df_orders.append(s_new_buy_order, ignore_index=True)
                try:
                    ts_todayp5 = ldt_timestamps[its+5]
                    s_new_sell_order = pd.DataFrame([{'timestamp':ts_todayp5, 'symbol':sym, 'action':'sell', 'shares':100}])
                    df_orders = df_orders.append(s_new_sell_order, ignore_index=True)
                except:
                    print "ldt_timestamps[its+5] not possible for ", ts_today
    df_orders.sort(columns='timestamp', inplace=True)
    return df_orders

def calculate_positions(f_start_cash, ls_symbols, df_orders, df_close):
    # Create data frame for positions.
    ldt_timestamps = df_close.index
    ls_columns = ['cash'] + ls_symbols
    df_positions = pd.DataFrame(0., index=ldt_timestamps, columns=ls_columns)
    # Update positions one day at a time.
    # TODO: don't use loops
    for its, ts_today in enumerate(ldt_timestamps):
        if its == 0:
            df_positions['cash'].ix[ts_today] = f_start_cash
        else:
            df_positions.ix[ts_today] = df_positions.ix[ts_yesterday]
        for iord, s_order in df_orders.iterrows():
            ts_order = s_order['timestamp']
            if ts_today == ts_order:
                act = s_order['action']
                sym = s_order['symbol']
                shr = s_order['shares']
                pri = df_close[sym].ix[ts_today]
                cash = df_positions['cash'].ix[ts_today]
                tot_shr = df_positions[sym].ix[ts_today]
                # TODO: positions.ix[ts_today, [sym]] causes TypeError. Why?
                if act == 'buy':
                    df_positions['cash'].ix[ts_today] = np.subtract(cash, np.dot(shr, pri))
                    df_positions[sym].ix[ts_today]    = np.add(tot_shr, shr)
                elif act == 'sell':
                    df_positions['cash'].ix[ts_today] = np.add(cash, np.dot(shr, pri))
                    df_positions[sym].ix[ts_today]    = np.subtract(tot_shr, shr)
                else:
                    print "ERROR: act neither buy nor sell."
                    print "act = ", act
        ts_yesterday = ts_today
    return df_positions

def calculate_values(ls_symbols, df_positions, df_close):
    """
    Calculate fund values.
    """

    # Write values from positions.
    ldt_timestamps = df_close.index
    df_values = pd.DataFrame(0., index=ldt_timestamps, columns=['value'])
    for its, ts_today in enumerate(ldt_timestamps):
        df_values['value'].ix[ts_today] = df_positions['cash'].ix[ts_today]
        # TODO: positions.ix[ts_today, [sym]] causes TypeError. Why?
        for sym in ls_symbols:
            f_stock_value = np.dot(df_positions[sym].ix[ts_today], df_close[sym].ix[ts_today])
            df_values['value'].ix[ts_today] = np.add(df_values['value'].ix[ts_today], f_stock_value)
    return df_values

def main():
    """
    Main function
    """

    # Reading the historical data.
    # dt_start = df_orders.index.min()
    print "dt_start = ", dt_start
    # dt_end = df_orders.index.max()
    print "dt_end = ", dt_end
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Import data.
    print "Import data."
    # Create an object of DataAccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')
    # Get a list of symbols we are going to trade
    list_name = 'sp5002012'
    ls_symbols = c_dataobj.get_symbols_from_list(list_name)
    ls_symbols.append('SPY')
    # ls_all_symbols = c_dataobj.get_all_symbols()
    # # Bad symbols are symbols present in portfolio but not in all symbols
    # ls_bad_symbols = list(set(ls_symbols) - set(ls_all_symbols))
    # if len(ls_bad_symbols) != 0:
    #     print "Orders contain bad symbols : ", ls_bad_symbols
    #     return
    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    # Copying the close price into separate DataFrame
    df_close = d_data['close'].copy()
    # Filling the gaps in data.
    for s_symbol in ls_symbols:
        df_close[s_symbol] = df_close[s_symbol].fillna(method='ffill')
        df_close[s_symbol] = df_close[s_symbol].fillna(method='bfill')
        df_close[s_symbol] = df_close[s_symbol].fillna(1.0)

    # Create events data frame.
    print "Finding events."
    df_events = find_events(ls_symbols, df_close, f_event_threshold)
    print "Writing events.csv."
    df_events.to_csv('events.csv')

    # Create orders data frame.
    print "Creating orders."
    df_orders = create_orders(ls_symbols, df_events)
    print "Writing orders.csv."
    df_orders.to_csv('orders.csv')

    # Calculate positions.
    print "Calculating positions."
    df_positions = calculate_positions(f_start_cash, ls_symbols, df_orders, df_close)
    print "Writing positions.csv."
    df_positions.to_csv('positions.csv')

    # Calculate fund value.
    print "Calculating fund values."
    df_values = calculate_values(ls_symbols, df_positions, df_close)
    print "Writing values.csv."
    values.to_csv('values.csv')

    # for fund
    na_price_fund = df_values['value'].values * 1.0
    na_normalized_price_fund = na_price_fund / na_price_fund[0, :]
    na_returns_fund = na_normalized_price_fund.copy()
    tsu.returnize0(na_returns_fund)
    daily_return_fund = na_returns_fund
    avg_daily_return_fund = np.average(daily_return_fund)
    std_daily_return_fund = np.std(daily_return_fund)
    # sharpe_ratio_fund = tsu.get_sharpe_ratio(rets=daily_ret_fund, risk_free=0.00)
    sharpe_ratio_fund = math.sqrt(252.0) * avg_daily_return_fund / std_daily_return_fund
    total_return_fund = na_normalized_price_fund[-1]
    
    # for comparision symbol
    # TODO: Flatten na_price list of lists.
    na_price_comp = df_close['SPY'].values * 1.0
    na_normalized_price_comp = na_price_comp / na_price_comp[0]
    na_returns_comp = na_normalized_price_comp.copy()
    tsu.returnize0(na_returns_comp)
    daily_return_comp = na_returns_comp
    avg_daily_return_comp = np.average(daily_return_comp)
    std_daily_return_comp = np.std(daily_return_comp)
    # sharpe_ratio_comp = tsu.get_sharpe_ratio(rets=daily_return_comp, risk_free=0.00)
    sharpe_ratio_comp = math.sqrt(252.0) * avg_daily_return_comp / std_daily_return_comp
    total_return_comp = na_normalized_price_comp[-1]

    print "sharpe_ratio_fund = ", sharpe_ratio_fund
    print "sharpe_ratio_comp = ", sharpe_ratio_comp

    print "total_return_fund = ", total_return_fund
    print "total_return_comp = ", total_return_comp

    print "std_daily_return_fund = ", std_daily_return_fund
    print "std_daily_return_comp = ", std_daily_return_comp

    print "avg_daily_return_fund = ", avg_daily_return_fund
    print "avg_daily_return_comp = ", avg_daily_return_comp

    return


if __name__ == '__main__':
    if len(sys.argv) == 1:
        f_start_cash = 50000.0
        # s_orders_filename = 'orders.csv'
        # s_values_filename = 'values.csv'
        f_event_threshold = 5.0
        dt_start = dt.datetime(2008, 01, 01, 16)
        dt_end   = dt.datetime(2009, 12, 31, 16)
        main()
    else:
        print "Usage: ./Homework_4.py"
