#! /bin/env python
"""
Homework 3
http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_3
Market simulation
Usage:
$ python marketsim.py 1000000 orders.csv values.csv
"""

import matplotlib
matplotlib.use('Agg')

import sys
import pandas as pd
import numpy as np

def main():
    # test that only 3 arguments
    # test that csv file exists
    # test that not overwriting another csv file
    [start_value, orders_file, values_file] = sys.argv[1:4]
    # loading text from: http://wiki.quantsoftware.org/index.php?title=QSTK_Tutorial_2
    orders = pd.read_csv(orders_file, header=False, names=['year', 'month', 'day', 'symbol', 'action', 'shares'],\
                             dtype={'year':int, 'month':int, 'day':int, 'symbol':str, 'action':str, 'shares':int})
    orders.to_csv(values_file, header=False, index=False, mode='a')
    # with open(values_file, "a") as vf:
    #     vf.write(start_value)
    #     vf.write("\n")
    return

if __name__ == '__main__':
    main()
