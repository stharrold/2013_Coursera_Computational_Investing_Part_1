#! /usr/bin/env python
"""
Homework 3
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
    dt_start = dt.datetime(2011, 1, 1)
    dt_end = dt.datetime(2011, 12, 31)
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Read in starting balance, file names, and orders
    [start_value, orders_file, values_file] = sys.argv[1:4]
    # loading text from: http://wiki.quantsoftware.org/index.php?title=QSTK_Tutorial_2
    orders = pd.read_csv(orders_file, header=False, names=['year', 'month', 'day', 'symbol', 'action', 'shares'],\
                             dtype={'year':int, 'month':int, 'day':int, 'symbol':str, 'action':str, 'shares':int})

    print orders.symbol.tolist()

    # # Creating an object of the dataaccess class with Yahoo as the source.
    # c_dataobj = da.DataAccess('Yahoo')

    # # Keys to be read from the data, it is good to read everything in one go.
    # ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # # Reading the data, now d_data is a dictionary with the keys above.
    # # Timestamps and symbols are the ones that were specified before.
    # ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    # d_data = dict(zip(ls_keys, ldf_data))

    # # Filling the data for NAN
    # for s_key in ls_keys:
    #     d_data[s_key] = d_data[s_key].fillna(method='ffill')
    #     d_data[s_key] = d_data[s_key].fillna(method='bfill')
    #     d_data[s_key] = d_data[s_key].fillna(1.0)

    # for every date between start date and end date
    # if date_today = date_action
    # if action = buy then value += shares*share_price
    # if action == sell then value -= shares*share_price

    # Write value
    # orders.to_csv(values_file, header=False, index=False, mode='a')
    # with open(values_file, "a") as vf:
    #     vf.write(start_value)
    #     vf.write("\n")
    return

if __name__ == '__main__':
    main()
