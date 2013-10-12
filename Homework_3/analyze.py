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
    print values
    na_price = values['value'].values
    print na_price
    na_normalized_price = na_price / na_price[0]
    na_rets = na_normalized_price.copy()
    tsu.returnize0(na_rets)
    daily_ret_portfolio = np.average(na_rets)
    std_daily_ret_portfolio = np.std(daily_ret_portfolio)

    print "std_daily_ret_portfolio = ", std_daily_ret_portfolio

    return

if __name__ == '__main__':
    main()
