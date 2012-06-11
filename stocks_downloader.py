#!/usr/bin/env python
#

from BeautifulSoup import BeautifulSoup as bs
from numpy import *
from collections import OrderedDict, defaultdict
from multiprocessing import Pool
import urllib2, sys, os, csv, re, time, datetime, filecmp, shutil
try: import cPickle as pickle
except: import pickle

csv_dir = 'stocks_csv'
stocks_fail = 'stocks_fail.txt'
stocks_CIK = 'stocks_CIK.txt'
dat_dir = 'stocks_dat'

def main():
	global csv_dir
	global stocks_fail
	global stocks_CIK

	download_flag = 0
	getcik_flag   = 0
	pickle_flag   = 1


	''' Name output directory for csv and ensure it is created '''

	if not os.path.exists(csv_dir):
		os.makedirs(csv_dir)


	''' DOWNLOAD MODULE '''
	if download_flag:

		# Get list of all stocks on the exchange
		with open('stocks_list.dat','r') as f:
			d = pickle.load(f)
		lst = d.keys()

		# Restore file that stores failed downloads
		open(stocks_fail, 'w').close()

		pool = Pool(processes=16)
		pool.map(downloader, lst)

		# notdone = list(set(lst).difference(set([i.replace('.csv','') for i in os.listdir(csv_dir)])))
		
		# Make sure all file names contain no spaces
		os.system('rename -v \'s/\ //g\' ' + csv_dir + '/*')

		# Delete all files that are size 0
		os.system('./cleaner.sh ' + csv_dir +'/')

		# Move all files that are duplicates into different directory
		lsdir = os.listdir(csv_dir); n = len(lsdir)
		collector = defaultdict(list);
		while len(lsdir) > 0:
			print (n-len(lsdir)), 'of', n
			i = lsdir.pop(0)
			f1 = csv_dir+'/'+i

			for j in lsdir:
				f2 = csv_dir+'/'+j
				if f1 != f2:
					if filecmp.cmp(f1,f2):
						collector[i].append(j)

		ref = []
		for k,v in collector.iteritems():
			if len(v) > 0:
				tup = [k]
				for i in v:
					tup.append(i)
				ref.append(tup)
		rmv = []
		for i in ref:
			i.remove(min(i, key=len))
			rmv = rmv + i
		# Make sure mv directory exists
		csv_mv_dir = 'stocks_csv_mv'
		if not os.path.exists(csv_mv_dir):
			os.makedirs(csv_mv_dir)
		for r in rmv:
			try: shutil.move(csv_dir+'/'+r, csv_mv_dir+'/'+r)
			except: pass


	''' Get list of directories downloaded '''
	lsdir = os.listdir(csv_dir); totl = len(lsdir)


	''' RECORD TICKER, CIK code pairs '''
	if getcik_flag:
		# Restore file that stores failed downloads
		open(stocks_CIK, 'w').close()

		pool = Pool(processes=20)
		pool.map(cikgetter, [i.replace('.csv','') for i in lsdir])

		# Combine files
		cpuoutputs = []
		for i in os.listdir('.'):
			if (stocks_CIK in i) & (len(i) > len(stocks_CIK) + 2):
				cpuoutputs.append(i)
		open('stocks_CIK_full.txt', 'w').close()
		writefile = open('stocks_CIK_full.txt','a')
		for i in cpuoutputs:
			with open(i,'r') as fr:
				interim = fr.read()
			writefile.write(interim)
		writefile.close()

		with open('stocks_CIK_full.txt','r') as f:
			d = f.read().split('\n')[:-1]
		ciked_list = []
		for i in d:
			ciked_list.append(i.split('\t')[0])

		notciked = list(set([i.replace('.csv','') for i in lsdir]).difference(set(ciked_list)))

		pool = Pool(processes=8)
		pool.map(cikgetter, notciked)

		# Re-Combine files
		cpuoutputs = []
		for i in os.listdir('.'):
			if (stocks_CIK in i) & (len(i) > len(stocks_CIK) + 2):
				cpuoutputs.append(i)
		open('stocks_CIK_full.txt', 'w').close()
		writefile = open('stocks_CIK_full.txt','a')
		for i in cpuoutputs:
			with open(i,'r') as fr:
				interim = fr.read()
			writefile.write(interim)
			os.remove(i)
		writefile.close()



	''' VECTORIZE DATA (make list of tuples) and STORE AS PICKLE '''
	if pickle_flag:
		# Name output directory for pickle and ensure it is created
		global dat_dir
		if not os.path.exists(dat_dir):
			os.makedirs(dat_dir)

		pool = Pool(processes=8)
		pool.map(pickler, [i.replace('.csv','') for i in lsdir])



def pickler(ticker):
	global dat_dir
	global csv_dir
	csv2pickle(ticker,csv_dir,dat_dir)
	print 'Pickled', ticker

def downloader(ticker):
	global csv_dir
	global stocks_fail

	# Download file, and return flag indicating
	dflag = download_csv(ticker, csv_dir)

	# Take action based on what flag is showed
	if dflag == 0:
		print 'Downloaded',ticker

	elif dflag == 2048:
		print 'Can\'t find ticker',ticker,'to download'
		os.system('rm ' + csv_dir + '/' + ticker + '.csv')

		with open(stocks_fail, 'a') as fal:
			fal.write(ticker + '\n')

	else:
		print 'Quitting downloader: non-resolved issue occured. OS error flag:', dflag
		exit()


def cikgetter(ticker):
	global stocks_CIK

	cik = get_CIK(ticker) # get CIK tuple
	#(CIK,name, {-1, if fail; 100, if traditional method; 0<=n<=99, means n words subtracted})

	# Write to file (ticker, company name, code, CIK)
	with open(stocks_CIK+str(os.getpid()), 'a') as fn:
		fn.write(ticker + '\t' + cik[1] + '\t' + str(cik[2]) + '\t' + cik[0] + '\n')

	# Take action based on CIK tuple flag
	print ticker,'\t',cik[2],'\t',cik[1],'\t',cik[0]


''' DOWNLOADS CSV FROM YAHOO '''
def download_csv(ticker,csv_dir):
	# Build URL string
	start_year = '1950'
	now = datetime.datetime.now()

	url_string = 'http://ichart.finance.yahoo.com/table.csv?'
	url_string += '&s=' + ticker.replace('&','%26')
	url_string += '&d=' + str(now.month-1)
	url_string += '&e=' + str(now.day)
	url_string += '&f=' + str(now.year)
	url_string += '&g=d&a=0&b=1&c=' + start_year
	url_string += '&ignore.csv'

	# Download file using system call
	return os.system('wget \'' + url_string + '\' -O \'' + csv_dir + '/' + ticker + '.csv\' -q')


''' Parses the CSV file and returns a tuple with data as a tuple of:
	(DATE, OPEN, HIGH, LOW, CLOSE, VOLUME) '''
def csv2pickle(ticker,csv_dir,dat_dir):
	with open(csv_dir+'/'+ticker+'.csv', 'rb') as f:
		fulldata = csv.reader(f)

		# Throw away header
		fulldata.next()

		# Temporarily store data in list to
		# adjust for dividends, splits, etc;
		DATE = []; OPEN = []; HIGH = []; LOW = []; CLOSE = []; VOL = []; ADJ = [];
		for row in fulldata:
			try:
				s = row[0].split('-')
				DATE.append(  (int(s[0]), int(s[1]), int(s[2])) )
				OPEN.append(  float(row[1]) )
				HIGH.append(  float(row[2]) )
				LOW.append(   float(row[3]) )
				CLOSE.append( float(row[4]) )
				VOL.append(   int(row[5])   )
				ADJ.append(   float(row[6]) )
			except IndexError:
				l = min(len(DATE),len(OPEN),len(HIGH),len(LOW),len(CLOSE),len(VOL),len(ADJ))
				DATE  = DATE[:l]
				OPEN  = OPEN[:l]
				HIGH  = HIGH[:l]
				LOW   = LOW[:l]
				CLOSE = CLOSE[:l]
				VOL   = VOL[:l]
				ADJ   = ADJ[:l]
				break

	# Carry out adjustment, then convert to our currency (mul by 100)
	OPENadj  = 100 * array(OPEN) * array(ADJ) / array(CLOSE)
	HIGHadj  = 100 * array(HIGH) * array(ADJ) / array(CLOSE)
	LOWadj   = 100 * array(LOW)  * array(ADJ) / array(CLOSE)
	CLOSEadj = 100 * array(ADJ)

	# Since the adjustment may divide by zero, we zero the Infs and NaNs
	OPENadj[ isinf(OPENadj) ] = 0.0; OPENadj[ isnan(OPENadj) ] = 0.0;
	HIGHadj[ isinf(HIGHadj) ] = 0.0; HIGHadj[ isnan(HIGHadj) ] = 0.0;
	LOWadj[  isinf(LOWadj)  ] = 0.0; LOWadj[  isnan(LOWadj)  ] = 0.0;

	# Make output list of tuples
	output = []
	for idx in xrange(len(DATE)):
		tup = ( DATE[idx], ( int(OPENadj[idx]),  int(HIGHadj[idx]), \
			int(LOWadj[idx]), int(CLOSEadj[idx]), VOL[idx]) )
		output.append(tup)

	# Reverse to normal chronological order, so 1st entry is oldest data
	output.reverse()

	# Convert to ordered dictionary
	output = OrderedDict(output)

	# Dump into pickle
	with open(dat_dir+'/'+ticker+'.dat', 'wb') as f:
		pickle.dump(output, f)


def get_CIK(ticker):
	# returns (0-flag or name, cik or list of ciks)
	soup = bs(urllib2.urlopen('http://www.sec.gov/cgi-bin/browse-edgar?company=&match=&CIK='+ticker+'&filenum=&State=&Country=&SIC=&owner=exclude&Find=Find+Companies&action=getcompany'))

	with open('stocks_list.dat','r') as f:
		nameF = pickle.load(f)[ticker] # full name of company

	try:
		cik = str(soup.findAll('link')[1].get('href').split('&CIK=')[1].split('&type=')[0])
		return (cik, nameF, 100)

	except IndexError:

		nameR = re.findall('[a-z&.-]+', nameF.lower()) # regex name of company

		if nameF == 'FAIL':
			return('FAIL',nameF,-1)
		else:
			cik2 = get_CIK2( nameR , len(nameR) )

			if cik2[0] == 1:
				return (cik2[1][0][0], nameF, len(nameR)-cik2[2])
			elif cik2[0] == -1:
				return (cik2[1][0][0], nameF, -1)
			else:
				return (str(cik2[1]), nameF, len(nameR)-cik2[2])
			#(CIK,name, {-1, if fail; 100, if traditional method; 0<=n<=99, means n words subtracted})

''' More robust method of grabbing CIKs '''
def get_CIK2(name,ngram):
	# Returns (number of CIKs, list of ciks [(CIK,name)] )
	if ngram > 0:

		soup = bs(urllib2.urlopen('http://www.sec.gov/cgi-bin/cik.pl.c?company=' + '+'.join(name[:ngram])))

		# Find how many search results on Edgar
		try:
			test = int(soup.find('strong').contents[0])
		except ValueError:
			test = int(soup.find('b').contents[0])
		except:
			test = 0

		if test == 0:
			return get_CIK2(name,ngram-1)

		else:
			l = soup.findAll('pre')[1].contents
			out = [];
			for (c, n) in zip(l[0::2], l[1::2]):
				out.append( (str(c.contents[0]), str(n).strip()) )
			return (len(l)/2, out, ngram)

	else:
		return (-1, [('FAIL','FAIL')],-1)

''' Return success rate for tuple (error, total) '''
def err(e,t):
	return '('+str(round((t-e)*100./t,2))+'%)'









'''
def get_prices(data,date):
	try:
		return (i for i in data if i[0] == date).next()
	except StopIteration:
		print 'No data for the date', date
		return None
'''


if __name__ == '__main__':
	main()
