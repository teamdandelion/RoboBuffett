#!/usr/bin/env python
import math

'''Notes:
The purpose of this module is to assign classification to (company, quarter, duration) tuples. The company will be represented by a unique company identifier and quarters will be represented as year, quarter tuples e.g. (2002,3) = 3Q2002. 
The classifier will assign a class to each tuple according to its performance, relative to other companies in the same industry, based on its relative performance during the period [filing date + 1, filing date + 1 + duration]. 

Company return  = ( company.close(filedate + duration) -  company.open(filedate + 1)) /  company.open(filedate + 1)
Industry return = (industry.close(filedate + duration) - industry.open(filedate + 1)) / industry.open(filedate + 1)
Classification is based on (company return - industry return)

The advantage to this classification approach is that it will capture idiosyncratic outperformance by companies relative to their peers, rather than macro-level economic trends.

Classification will be based on threshold return levels, which will be expressed as an ordered list [t1, t2, t3]. The (c,q,d) tuple will be assigned to the first threshold for which relative return <= threshold level, where assignment means returning the 0-based index of the threshold. If the return is greater than the maximum threshold level, then it will return the index of the max threshold + 1 (i.e. returns len(thresholds)). 
'''

thresholds = [-.4, .15] # Represents 3 classes: (-Inf, -40%), (-40%, 15%), (15%, Inf)
durations = [1, 20, 40]
# Returns compared to threshold values are annualized returns relative to industry, rather than raw rates of return 

def annualize_return(rate_of_return, duration):
    # This attempts to account for the opportunity cost of capital, i.e. getting a 10% return on a 1-month holding is generally better than a 15% return on a 6-month holding. However, this is imperfect because the opportunity cost is properly a function of how many other documents are coming out in the near future, how likely we are to want to buy those stocks, etc. So if documents are evenly spaced throughout the year, so that on average we want to buy a stock every week, we shouldn't necessarily favor 1-day holding periods over 2-day holding periods (as this model would heavily favor). However if all documents are released in 1-week periods every quarter then we should really want short holding periods. If we invest over medium to long term periods (e.g. 2 months) then this is less of an issue.
    trading_days_per_year = 252
    return rate_of_return ** (trading_days_per_year/float(duration))

def training_classification(company, date, durations, thresholds):
    ticker = company.ticker
    SIC    = company.SIC
    #sector = company.sector
    start  = next_trading_day(ticker, date)
    # Requires a next_trading_day module
    classifications = []
    for duration in durations:
        try:
            stock_return  = get_stock_return(ticker, start, end)
            sic_return    = get_sic_return(SIC, start, end)
            # sector_return = get_sector_return(sector, start, end)
            # baseline_return = weight_sicsector(SIC, sic_return, sector, sector_return)
            relative_return = stock_return - sic_return
            ann_relative_return = annualize_return(relative_return, duration)
            classif = threshold_sieve(ann_relative_return, thresholds)
            classifications.append(classif)
        except StockRangeError:
            classifications.append(None)

def threshold_sieve(val, thresholds):
    for i in xrange(len(thresholds)):
        if val <= thresholds[i]:
            return i
    return i+1


def create_classification_set(manager, thresholds, durations):
    # Take a manager, thresholds, durations
    # Choose a 'training set' of Company/Date pairs (i.e. document references)
    # Generate a classification set for each duration
    # Classify each Company/Date pair into a threshold group for each duration
    # Return the d sets (d = |durations|)
    

def generate_classification_model(TODO):
    # Take a classification set and the manager
    # Generate a group dictionary for the set
    # Adjust for psuedocount
    pass

def classify_multinomial(text, groups, psuedocount):
    """Classifies a text into one of the provided groups, given a psuedocount.
    
    Returns a tuple containing the chosen group and the difference in log-
    likelihood between the chosen group and the second best option 
    (for validation purposes and perhaps confidence estimation).
    
    """
    comparisons = {}
    for group in groups:
        comparisons[group] = likelihood_comparison(text, group, psuedocount)    
    max  = float("-inf")
    second_max = float("-inf")
    
    #Want to find the maximum LLV (to classify the group) and the second-maximum
    #LLV (to report the difference)
    for group in comparisons:
        if comparisons[group] > second_max:
            if comparisons[group] > max:
                second_max = max
                max = comparisons[group]
                classification = group
            else:
                second_max = comparisons[group]
    
    diff = max - second_max
    assert diff > 0
    return (classification, diff, max)
        
        
def multinomial_LLV(text, (group_dict, wordcount), psuedocount):
    """Generates log-likelihood that given Text came from given TextGroup.
    
    Note that likelihood function has no absolute meaning, since it is a log-
    likelihood with constants disregarded. Instead, the return value may be 
    used as a basis for comparison to decide which TextGroup is more likely to 
    contain the Text. 
    
    """
    #Make local copies of the dictionaries so we can alter them without causing problems
    theta_dict = copy.copy(group_dict)
    
    #DO psuedocount biasing beforehand

    numWords = float(wordcount + psuedocount * len(group_dict))
    # Need to add psuedocounts since log(0) is undefined (or in orig. multinomial model abset the log transformation, multiplying by a 0 factor would force the result to 0)
    for word in theta_dict:
        theta_dict[word] += psuedocount
    for word in text.dict:
        if word not in theta_dict:
            theta_dict[word] = psuedocount
            numWords += psuedocount
    theta = {}
    for word in theta_dict:
        theta[word] = theta_dict[word] / numWords

    loglikelihood = 0
    for word in text.dict:
        loglikelihood += text.dict[word] * math.log(theta[word])                
    return loglikelihood



