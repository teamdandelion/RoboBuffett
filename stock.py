"""Handles using stock prices that have already been scraped"""
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


def get_open(ticker, date):
    #return a price on that date, or an exception if undefined

def get_close(ticker, date):

def get_volume(ticker, date):

def get_marketcap(ticker, date):
    # Return market cap on closest defined day, raise an exception if not defined at all in a 12 month span