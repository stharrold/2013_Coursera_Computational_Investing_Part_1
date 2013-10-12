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

    # loading text from: http://wiki.quantsoftware.org/index.php?title=QSTK_Tutorial_2
    values_unindexed = pd.read_csv(orders_file, header=False, names=['year', 'month', 'day', 'values'],\
                             dtype={'year':int, 'month':int, 'day':int, 'symbol':str, 'action':str, 'shares':int})
    ls_symbols = list(set([s.strip(' ') for s in orders_unindexed.symbol.tolist()]))
    return

if __name__ == '__main__':
    main()
