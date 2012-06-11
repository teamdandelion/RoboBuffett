#!/usr/bin/env python

import os, collections, datetime
try: import cPickle as pickle
except: import pickle

"""Handles using stock prices that have already been scraped"""
#CIKs are *string* values. Considered storing as ints but CIKs are 10-digit, could potentially overflow 32-bit ints. Since we never do arithmetic on them, and only use them is index keys, better to use strings.

#Tickers will be (Exchange, Ticker) tuples, e.g. ('NYSE', 'GS').

#Prices will be integer values with 100 = $1 conversion. Thus Apple's price of $558.22 becomes 55822.

# 'data' outputed is in form (open, high, low, close, volume)

def ticker_to_CIK(ticker):
	''' Return CIK if valid ticker, return None otherwise '''
	with open('validated_CIK.dat') as f:
		d = pickle.load(f)
	try: return [i[1] for i in d if i[0] == ticker][0]
	except IndexError: return None

def CIK_to_ticker(CIK):
	''' Return ticker if valid CIK, return None otherwise '''
	with open('validated_CIK.dat') as f:
		d = pickle.load(f)
	try: return [i[0] for i in d if i[1] == CIK][0]
	except IndexError: return None

def good_CIKs():
	''' Return list of all CIKs for which we have trading info on. '''
	with open('validated_CIK.dat') as f:
		d = pickle.load(f)
	return [i[1] for i in d]

def good_tickers():
	''' Return list of all tickers for which we have trading info on. '''
	with open('validated_CIK.dat') as f:
		d = pickle.load(f)
	return [i[0] for i in d]

def get_open(ticker, dates):
	''' Return a price on that date, or the next available day 	'''
	''' Returns list of (date, price) tuples 					'''
	if isinstance(dates,list):
		return [(i[0],i[1][0]) for i in get_data(ticker,dates)]
	elif isinstance(dates,tuple):
		return [(i[0],i[1][0]) for i in [get_datum(ticker,dates)]]
	else:
		return (None,None)

def get_close(ticker, dates):
	''' Return a price on that date, or the next available day 	'''
	''' Returns list of (date, price) tuples					'''
	if isinstance(dates,list):
		return [(i[0],i[1][3]) for i in get_data(ticker,dates)]
	elif isinstance(dates,tuple):
		return [(i[0],i[1][3]) for i in [get_datum(ticker,dates)]]
	else:
		return (None,None)

def get_volume(ticker, dates):
	''' Return volume on that date, or the next available day 	'''
	''' Returns list of (date, volume) tuples					'''
	if isinstance(dates,list):
		return [(i[0],i[1][4]) for i in get_data(ticker,dates)]
	elif isinstance(dates,tuple):
		return [(i[0],i[1][4]) for i in [get_datum(ticker,dates)]]
	else:
		return (None,None)

def get_data(ticker, dates):
	out_list = []
	for d in dates:
		out_list.append(get_datum(ticker,d))
	return out_list

def get_datum(ticker, date):
	''' Return a price on that date, or the next available day 	'''
	''' Returns (date, price) tuple 							'''
	# Check if file exists
	if os.path.isfile('stocks_dat/'+ticker+'.dat'):
		with open('stocks_dat/'+ticker+'.dat','r') as f:
			d = pickle.load(f)
		try: return (date, d[date])
		# (exception) If date entry does not exist, try next day
		except KeyError: return get_datum(ticker, get_nextday(date))
		# (any other exception) return None
		else: return (None, None)
	else:
		return (None, None)

def get_nextday(date):
	n = datetime.date(date[0],date[1],date[2]) + datetime.timedelta(days=1)
	return (n.year, n.month, n.day)

def get_marketcap(ticker, date):
	# Return market cap on closest defined day, raise an exception if not defined at all in a 12 month span
	'''	WORK ON THIS '''
	return None
