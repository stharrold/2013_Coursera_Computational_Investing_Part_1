#! /usr/bin/env python
"""
Homework 3, Part 1
http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_3
Market simulation
Usage:
$ python marketsim.py 1000000 orders.csv values.csv
"""

import matplotlib
matplotlib.use('Agg')

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import csv
import sys
import pandas as pd
import numpy as np
import datetime as dt

def main():

    # TODO:
    # test that only 3 arguments
    # test that csv file exists
    # test that not overwriting another csv file

    # Start and end dates
    dt_start = dt.datetime(2011, 1, 10, 16)
    dt_end = dt.datetime(2011, 12, 20, 16)
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Read in starting cash balance, file names, and orders
    [cash_initial, orders_file, values_file] = sys.argv[1:4]
    # loading text from: http://wiki.quantsoftware.org/index.php?title=QSTK_Tutorial_2
    orders = pd.read_csv(orders_file, header=None, names=['year', 'month', 'day', 'symbol', 'action', 'shares'])
    #                             dtype={'year':int, 'month':int, 'day':int, 'symbol':str, 'action':str, 'shares':int})
    for i, order in orders.iterrows():
        orders['symbol'].ix[i] = order['symbol'].strip(' ').upper()
        orders['action'].ix[i] = order['action'].strip(' ').lower()
    ls_symbols = list(set(orders['symbol'].tolist()))

    # Fetch stock data and fill in NANs.
    c_dataobj = da.DataAccess('Yahoo')
    # ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ls_keys = ['actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

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
            ts_order = dt.datetime(order['year'], order['month'], order['day'], 16)
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

    # Write values from positions.
    values = pd.DataFrame(0., index = ldt_timestamps, columns = ['year', 'month', 'day', 'value'])
    for its, ts_today in enumerate(ldt_timestamps):
        values['year'].ix[ts_today]  = ts_today.year
        values['month'].ix[ts_today] = ts_today.month
        values['day'].ix[ts_today]   = ts_today.day
        values['value'].ix[ts_today] = positions['cash'].ix[ts_today]
        # TODO: positions.ix[ts_today, [sym]] causes TypeError. Why?
        for sym in ls_symbols:
            values['value'].ix[ts_today] += positions[sym].ix[ts_today] * d_data['actual_close'][sym].ix[ts_today]
    values.to_csv(values_file)

    return

if __name__ == '__main__':
    main()
