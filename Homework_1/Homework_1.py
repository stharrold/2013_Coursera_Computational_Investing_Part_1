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
import numpy as np

def main():

    # Start and End date of the charts
    # Example 1:
    # dt_start = dt.datetime(2010, 1, 1)
    # dt_end = dt.datetime(2010, 12, 31)
    # Example 2:
    # dt_start = dt.datetime(2011, 1, 1)
    # dt_end = dt.datetime(2011, 12, 31)
    # Question 1:
    # dt_start = dt.datetime(2011, 1, 1)
    # dt_end = dt.datetime(2011, 12, 31)
    # Question 2:
    dt_start = dt.datetime(2011, 1, 1)
    dt_end = dt.datetime(2011, 12, 31)

    # List of symbols
    # Example 1:
    # ls_symbols = ['AAPL', 'GLD', 'GOOG', 'XOM']
    # Example 2:
    # ls_symbols = ["AXP", "HPQ", "IBM", "HNZ"]
    # Question 1:
    # ls_symbols = ['BRCM', 'TXN', 'AMD', 'ADI']
    # Question 2:
    ls_symbols = ['AAPL', 'GOOG', 'IBM', 'MSFT'] 

    # Allocation
    # Example 1:
    # allocation = [0.4, 0.4, 0.0, 0.2]
    # Example 2:
    # allocation = [0.0, 0.0, 0.0, 1.0]
 
    allocation = [0.2, 0.2, 0.3, 0.3]
    original_unallocated_fraction = 1.
    fraction_step = 0.1
    old_sharpe = 0.
    for stock0_fraction in np.arange(0., original_unallocated_fraction + fraction_step, fraction_step):
        allocation[0] = stock0_fraction
        unallocated_fraction = original_unallocated_fraction - np.sum(allocation[:1])
        for stock1_fraction in np.arange(0., unallocated_fraction + fraction_step, fraction_step):
            allocation[1] = stock1_fraction
            unallocated_fraction = original_unallocated_fraction - np.sum(allocation[:2])
            for stock2_fraction in np.arange(0., unallocated_fraction + fraction_step, fraction_step):
                allocation[2] = stock2_fraction
                unallocated_fraction = original_unallocated_fraction - np.sum(allocation[:3])
                stock3_fraction = unallocated_fraction
                allocation[3] = stock3_fraction
                if np.sum(allocation) != 1.:
                    print "ERROR: np.sum(allocation) != 1"
                (sharpe_ratio_portfolio, std_daily_ret_portfolio, avg_daily_ret_portfolio, yearly_ret_portfolio) \
                    = simulate(dt_start, dt_end, ls_symbols, allocation)
                new_sharpe = sharpe_ratio_portfolio.copy()
                if new_sharpe > old_sharpe:
                    print "new_sharpe = ", new_sharpe
                    opt_allocation = allocation[:]
                    print "allocation = ", opt_allocation
                    (opt_sharpe_ratio_portfolio, opt_std_daily_ret_portfolio, opt_avg_daily_ret_portfolio, opt_yearly_ret_portfolio) = \
                        (sharpe_ratio_portfolio, std_daily_ret_portfolio, avg_daily_ret_portfolio, yearly_ret_portfolio)[:]
                    old_sharpe = new_sharpe

    # Print output
    print "dt_start = ", dt_start
    print "dt_end = ", dt_end
    print "ls_symbols = ", ls_symbols
    print "allocation = ", opt_allocation
    print "sharpe_ratio = ", opt_sharpe_ratio_portfolio
    print "std_daily_ret_portfolio = ", opt_std_daily_ret_portfolio
    print "avg_daily_ret_portfolio = ", opt_avg_daily_ret_portfolio
    print "yearly_ret_portfolio = ", opt_yearly_ret_portfolio

def simulate(dt_start, dt_end, ls_symbols, allocation):
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values

    # Compute normalized daily returns

    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]

    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = na_normalized_price.copy()

    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_rets)

    # Compute average daily return of the total portfolio
    # Compute standard deviation of daily returns of the total portfolio
    daily_ret_portfolio = np.average(na_rets, axis=1, weights=allocation)
    avg_daily_ret_portfolio = np.average(daily_ret_portfolio)
    std_daily_ret_portfolio = np.std(daily_ret_portfolio)

    # Compute sharpe ratio (252 trading days in year, risk free rate = 0)
    sharpe_ratio_portfolio = tsu.get_sharpe_ratio(rets=daily_ret_portfolio, risk_free=0.00)

    # Compute return of the total portfolio
    yearly_ret_portfolio = np.average(na_normalized_price[-1], weights=allocation)

    return (sharpe_ratio_portfolio, std_daily_ret_portfolio, avg_daily_ret_portfolio, yearly_ret_portfolio)

if __name__ == '__main__':
    main()
