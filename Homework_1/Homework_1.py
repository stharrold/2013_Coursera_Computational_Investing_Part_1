#! /usr/bin/env python

'''
Homework 1
http://wiki.quantsoftware.org/index.php?title=CompInvestI_Homework_1

Changelog:
09/15/2013: Created by Samuel Harrold (STH).
'''

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

def main():

    # List of symbols
    ls_symbols = ["AAPL", "GLD", "GOOG", "XOM"]

    # Start and End date of the charts
    dt_start = dt.datetime(2011, 1, 1)
    dt_end = dt.datetime(2011, 12, 31)



    # Compute normalized daily returns


    # Compute standard deviation of daily returns of the total portfolio


    # Compute average daily return of the total portfolio


    # Compute sharpe ratio (252 trading days in year, risk free rate = 0)
    # tsu.getSharpeRatio(naRets, fFreeReturn=0.00)

    # Compute return of the total portfolio

if __name__ == '__main__':
    main()
