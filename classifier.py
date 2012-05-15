#!/usr/bin/env python

'''Notes:
The purpose of this module is to assign classification to (company, quarter, duration) tuples. The company will be represented by a unique company identifier and quarters will be represented as year, quarter tuples e.g. (2002,3) = 3Q2002. 
The classifier will assign a class to each tuple according to its performance, relative to other companies in the same industry, based on its relative performance during the period [filing date + 1, filing date + 1 + duration]. 

Company return  = ( company.close(filedate + duration) -  company.open(filedate + 1)) /  company.open(filedate + 1)
Industry return = (industry.close(filedate + duration) - industry.open(filedate + 1)) / industry.open(filedate + 1)
Classification is based on (company return - industry return)

The advantage to this classification approach is that it will capture idiosyncratic outperformance by companies relative to their peers, rather than macro-level economic trends.

Classification will be based on threshold return levels, which will be expressed as an ordered list [t1, t2, t3]. The (c,q,d) tuple will be assigned to the first threshold for which relative return <= threshold level, where assignment means returning the 0-based index of the threshold. If the return is greater than the maximum threshold level, then it will return the index of the max threshold + 1 (i.e. returns len(thresholds)). 
'''

thresholds = [-.6, -.4, -.2, 0, .2, .4, .6, .8, 1]
durations = [1, 5, 20, 40, 80, 160, 240, 480]
# 1 day, 1 week, 1 month, 2 month, 4 month, 8 month, 12 month, 24 month
# Returns compared to threshold values are annualized returns relative to industry, rather than raw rates of return 

def annualize_return(rate_of_return, duration):
    # This attempts to account for the opportunity cost of capital, i.e. getting a 10% return on a 1-month holding is generally better than a 15% return on a 6-month holding. However, this is imperfect because the opportunity cost is properly a function of how many other documents are coming out in the near future, how likely we are to want to buy those stocks, etc. So if documents are evenly spaced throughout the year, so that on average we want to buy a stock every week, we shouldn't necessarily favor 1-day holding periods over 2-day holding periods (as this model would heavily favor). However if all documents are released in 1-week periods every quarter then we should really want short holding periods. If we invest over medium to long term periods (e.g. 2 months) then this is less of an issue.
    trading_days_per_year = 252
    return rate_of_return ** (trading_days_per_year/float(duration))

def training_classification(company, document, durations, thresholds):
    ticker = company.ticker
    SIC    = company.SIC
    sector = company.sector
    start  = next_trading_day(document.filingdate)
    # Requires a next_trading_day module
    classifications = []
    for duration in durations:
        try:
            stock_return  = get_stock_return(ticker, start, end)
            sic_return    = get_sic_return(SIC, start, end)
            sector_return = get_sector_return(sector, start, end)
            baseline_return = weight_sicsector(SIC, sic_return, sector, sector_return)
            relative_return = stock_return - baseline_return
            ann_relative_return = annualize_return(relative_return, duration)
            classif = threshold_sieve(ann_relative_return, thresholds)
            classifications.append(classif)
        except FutureError:
            classifications.append(None)

def threshold_sieve(val, thresholds):
    for i in xrange(len(thresholds)):
        if val <= thresholds[i]:
            return i
    return i+1



