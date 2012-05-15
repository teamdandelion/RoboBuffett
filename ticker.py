"""Handles conversions from tickers to CIKs and vice versa"""

#CIKs are *string* values. Considered storing as ints but CIKs are 10-digit, could potentially overflow 32-bit ints. Since we never do arithmetic on them, and only use them is index keys, better to use strings.

#Tickers will be (Exchange, Ticker) tuples, e.g. ('NYSE', 'GS').

def ticker_to_CIK(ticker):
    #TODO: Define this function
    #Return CIK if valid ticker, raise an error otherwise
    return 0

def CIK_to_ticker(CIK):
    return 0

def good_CIKs():
    # Return list of all CIKs for which we have trading info on.

