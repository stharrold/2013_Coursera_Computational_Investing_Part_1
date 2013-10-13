#! /usr/bin/env python
"""
Homework 3, Part 2
http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_3
Analyze performance
Usage:
$ python analyze.py values.csv \$SPX
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

    # Read in starting cash balance, file names, and orders
    [values_file, comp_symbol] = sys.argv[1:3]
    # loading text from: http://wiki.quantsoftware.org/index.php?title=QSTK_Tutorial_2
    values = pd.read_csv(values_file, index_col=0)

    # from Homework 2
    # TODO: Correct bad naming conventions for values.
    # TODO: make into function for comparision with S&P

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
    # Fetch stock data and fill in NANs.
    c_dataobj = da.DataAccess('Yahoo')
    # Start and end dates
    # TODO: Get from values.csv
    dt_start = dt.datetime(2011, 1, 10, 16)
    dt_end = dt.datetime(2011, 12, 20, 16)
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    ls_symbols = [comp_symbol]
    # ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ls_keys = ['actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    # TODO: Flatten na_price list of lists.
    na_price = d_data['actual_close'].values
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

if __name__ == '__main__':
    main()
