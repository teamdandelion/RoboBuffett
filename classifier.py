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





def threshold_classification(company_quarter, duration, thresholds)
