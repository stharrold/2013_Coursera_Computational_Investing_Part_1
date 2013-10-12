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
    dt_start = dt.datetime(2008, 12, 1)
    dt_end = dt.datetime(2008, 12, 31)
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Read in starting cash balance, file names, and orders
    [cash_initial, orders_file, values_file] = sys.argv[1:4]
    # loading text from: http://wiki.quantsoftware.org/index.php?title=QSTK_Tutorial_2
    orders_unindexed = pd.read_csv(orders_file, header=False, names=['year', 'month', 'day', 'symbol', 'action', 'shares'],\
                             dtype={'year':int, 'month':int, 'day':int, 'symbol':str, 'action':str, 'shares':int})
    ls_symbols = list(set([s.strip(' ') for s in orders_unindexed.symbol.tolist()]))

    # Reindex orders.
    # TODO: don't loop.
    new_index = []
    for idx, row in orders_unindexed.iterrows():
        new_index += [dt.datetime(row['year'],
                                  row['month'],
                                  row['day'],
                                  16)]
    orders = orders_unindexed.reindex(index = new_index, columns = ['symbol', 'action', 'shares'])
    for idx, row in orders_unindexed.iterrows():
        orders['symbol'].ix[idx] = row['symbol'].strip(' ')
        orders['action'].ix[idx] = row['action'].strip(' ')
        orders['shares'].ix[idx] = row['shares']

    # Fetch stock data and fill in NANs.
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
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
    # for idx, pos in positions.iterrows():
    for i, ts_today in enumerate(ldt_timestamps):
        if i == 0:
            positions['cash'].ix[ts_today] = cash_initial
        else:
            ts_yesterday = ldt_timestamps[i-1]
            positions.ix[ts_today] = positions.ix[ts_yesterday]
        for ts_order, order in orders.iterrows():
            if ts_today == ts_order:
                act = orders['action'].ix[ts_today]
                sym = orders['symbol'].ix[ts_today]
                shr = orders['shares'].ix[ts_today]
                pri = d_data['actual_close'][sym].ix[ts_today]
                if act == 'BUY':
                    positions['cash'].ix[ts_today] -= shr*pri
                    positions[sym].ix[ts_today] += shr
                else:
                    positions['cash'].ix[ts_today] += shr*pri
                    positions[sym].ix[ts_today] -= shr

    # Write values from positions.
    values = np.zeros((len(ldt_timestamps), 4))
    for i, ts_today in enumerate(ldt_timestamps):
        values[i, 0] = ts_today.year
        values[i, 1] = ts_today.month
        values[i, 2] = ts_today.day
        values[i, 3] = positions['cash'].ix[ts_today]
        for sym in ls_symbols:
            values[i, 3] += positions.ix[ts_today, [sym]]*d_data['actual_close'].ix[ts_today, [sym]]

    print values

    np.savetxt(values_file, values, delimiter=",")

    # positions.to_csv(values_file, header=False, index=False)
    # with open(values_file, "a") as vf:
    #     vf.write(start_value)
    #     vf.write("\n")

    return

if __name__ == '__main__':
    main()
