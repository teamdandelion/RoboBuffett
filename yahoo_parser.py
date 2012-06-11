#!/usr/bin/env python
#

from BeautifulSoup import BeautifulSoup as bs
from collections import defaultdict
from multiprocessing import Pool
import urllib2
try: import cPickle as pickle
except: import pickle

def main():
	download_list = 0
	validate_list = 0
	compile_list  = 0


	''' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - '''
	fulllistdat = 'raw_stocks_list.dat'
	if download_list:
		maximum = 23686; cnt = 1; fcnt = 1; collector = defaultdict(list);
		while cnt < maximum:
			soup = bs(urllib2.urlopen('http://screener.finance.yahoo.com/b?pr=0/&s=tk&vw=1&db=stocks&b=' + str(cnt)))
			table = soup.findAll("table")[1].contents[1].contents[1].contents[1]
			for n in range(21)[1:]:
				try:
					ticker = str(table.contents[n].find('a').string).replace(';','')
					name = str(table.contents[n].findAll('font')[1].string).replace('&amp;','&')
					collector[ticker] = name
					print fcnt,'of',maximum,'\t',ticker,'\t',name
					fcnt += 1
				except:
					saver(collector, fulllistdat)
			cnt += 20
		saver(collector, fulllistdat)




	''' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - '''
	# Load pickled stocks data
	with open(fulllistdat) as f:
		d = pickle.load(f)

	if validate_list:
		# Clear file in which we record validation tickers
		open('record_stock_name_validation.txt', 'w').close()

		pool = Pool(processes=16)
		pool.map(validator, d.keys())



	''' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - '''
	if compile_list:
		with open('raw_name_validation.txt', 'r') as f:
			rcrd = f.read().split('\n')[:-1]
		collector = defaultdict(list)
		for i in rcrd:
			collector[i.split('\t')[0]] = i.split('\t')[1]
		notdone = list(set(d.keys()).difference(set(collector.keys())))
		
		pool = Pool(processes=8)
		pool.map(validator, notdone)

		final_list = defaultdict(list)
		p = 0; n = 0; f = 0; r = 0;
		for k,v in collector.iteritems():
			if v == '':
				n += 1
			elif v == 'FAIL':
				f += 1
			elif v == 'PASS':
				final_list[k] = d[k]
				p += 1
			else:
				final_list[v] = d[k]
				r += 1

		with open('stocks_list.dat','wb') as fn:
			pickle.dump(dict(final_list),fn)

		print 'Total list:',len(final_list)
		print 'Nothing:',n,'| Fail:',f,'| Pass:',p,'| Replace:',r
			

def validator(ticker):
	soup = bs(urllib2.urlopen('http://finance.yahoo.com/q?s=' + ticker.replace('&','%26') ))

	outcome = ''

	try:
		if ( str(soup.find('h3').contents[0]) == 'Changed Ticker Symbol' ):
			outcome = str(soup.findAll('p')[1].contents[1].contents[0])
	except: pass

	try:
		if ( str(soup.findAll('h2')[2].contents[0]) == 'There are no All Markets results for' ):
			outcome = 'FAIL'
	except: pass

	try:
		tname = str(soup.findAll('h2')[3].contents[0]).split('(')[-1][:-1]
		# tname = fname[fname.find("(")+1:fname.find(")")]
		if ticker in tname:
			if ticker == tname:
				outcome = 'PASS'
			else:
				outcome = tname
	except: pass

	with open('raw_name_validation.txt','a') as f:
		f.write(ticker+'\t'+outcome+'\n')

	print ticker,'\t',outcome

def saver(collector, fname):
	with open(fname,'wb') as f:
		pickle.dump(dict(collector),f)

if __name__ == '__main__':
	main()
