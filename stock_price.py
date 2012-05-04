#!/usr/bin/env python
#

from datetime import datetime
from string import lower, upper
import os, csv

def main():
	# Input stock
	ticker = lower('AAPL')

	# If output directory doesn't exist, make it
	output_dir = 'stock_data'
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	# If stock CSV isn't downloaded, DOWNLOAD it
	if os.path.isfile(output_dir+"/"+ticker+".csv"):
		print upper(ticker) + " data already exists in this directory.\n"
	else:
		download_csv(ticker,output_dir)

	# Run this code to download all S&P 500 files
	"""
	for s in snp_list():
		download_csv(s,output_dir)
	"""

	# Now that the CSV data is downloaded,
	# arrange it into a tuple
	data = vectorize_csv(ticker,output_dir)

	# # # # TEST EXAMPLES # # # #

	# Test to see if the tuples have been created
	print "Here are the first few lins of the data tuple output:"
	print "Format: (DATE, OPEN, HIGH, LOW, CLOSE, VOLUME)"
	print data[1:5]

	# Retrieve price for specific date
	sample_date = (2012,1,18);
	print "\nFind price on:", sample_date, "\n", get_prices(data,sample_date)
	sample_date = (2012,1,21);
	print "\nFind price on:", sample_date, "\n", get_prices(data,sample_date)


# Parses the CSV file and returns a tuple with data
# as a tuple of:
# (DATE, OPEN, HIGH, LOW, CLOSE, VOLUME) 
def vectorize_csv(ticker,output_dir):
	fulldata = csv.reader(open(output_dir+'/'+ticker+'.csv', 'rb'))
	output = []

	# Throw away header
	fulldata.next()

	# Store rest of data in list of tuples
	for row in fulldata:
		s = row[0].split('-')
		tup = ((int(s[0]), int(s[1]), int(s[2])), float(row[1]), \
			float(row[2]), float(row[3]), float(row[4]), int(row[5]), \
			float(row[6]))
		output.append(tup)

	# Adjust for dividends, splits, etc.
	"""
	DATEtemp{ptr,1} = DATEvar;
	OPENtemp(ptr,1) = OPENvar  * adj_close / CLOSEvar;
	HIGHtemp(ptr,1) = HIGHvar  * adj_close / CLOSEvar;
	LOWtemp (ptr,1) = LOWvar   * adj_close / CLOSEvar;
	CLOSEtemp(ptr,1)= CLOSEvar * adj_close / CLOSEvar;
	VOLtemp(ptr,1)  = VOLvar;
	"""

	# Reverse to normal chronological order, so 1st entry is oldest data
	output.reverse()	
	return output
	

# Downloads CSV file and stores it in the
# respective directory
def download_csv(ticker,output_dir):
	# Build URL string
	start_year = '1950'
	now = datetime.now()

	url_string = 'http://ichart.finance.yahoo.com/table.csv?'
	url_string += '&s=' + (ticker)
	url_string += '&d=' + str(now.month-1)
	url_string += '&e=' + str(now.day)
	url_string += '&f=' + str(now.year)
	url_string += '&g=d&a=0&b=1&c=' + start_year
	url_string += '&ignore.csv'

	# Download file using system call
	os.system("wget \'" + url_string + "\' -O \'" + output_dir + "/" + (ticker) + ".csv\'")

	print "Finished downloading " + upper(ticker) + "\n"

def get_prices(data,date):
	try:
		return (i for i in data if i[0] == date).next()
	except StopIteration:
		print "No data for the date", date
		return None


# Simply gives the list of stocks on S&P 500
# Kept this function at the bottom due to size
def snp_list():
	return ['MMM', 'ACE', 'ABT', 'ANF', 'ACN', 'ADBE', 'AMD', 'AES', 'AET', 'AFL', 'A', 'GAS', 'APD', 'ARG', 'AKAM', 'AA', 'ATI', 'AGN', 'ALL', 'ALTR', 'MO', 'AMZN', 'AEE', 'AEP', 'AXP', 'AIG', 'AMT', 'AMP', 'ABC', 'AMGN', 'APH', 'APC', 'ADI', 'AON', 'APA', 'AIV', 'APOL', 'AAPL', 'AMAT', 'ADM', 'AIZ', 'T', 'ADSK', 'ADP', 'AN', 'AZO', 'AVB', 'AVY', 'AVP', 'BHI', 'BLL', 'BAC', 'BK', 'BCR', 'BAX', 'BBT', 'BEAM', 'BDX', 'BBBY', 'BMS', 'BRK.B', 'BBY', 'BIG', 'BIIB', 'BLK', 'HRB', 'BMC', 'BA', 'BWA', 'BXP', 'BSX', 'BMY', 'BRCM', 'BF.B', 'CHRW', 'CA', 'CVC', 'COG', 'CAM', 'CPB', 'COF', 'CAH', 'CFN', 'KMX', 'CCL', 'CAT', 'CBG', 'CBS', 'CELG', 'CNP', 'CTL', 'CERN', 'CF', 'SCHW', 'CHK', 'CVX', 'CB', 'CI', 'CINF', 'CTAS', 'CSCO', 'C', 'CTXS', 'CLF', 'CLX', 'CME', 'CMS', 'COH', 'KO', 'CCE', 'CTSH', 'CL', 'CMCSA', 'CMA', 'CSC', 'CAG', 'COP', 'CNX', 'ED', 'STZ', 'CEG', 'GLW', 'COST', 'CVH', 'COV', 'CSX', 'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA', 'DF', 'DE', 'DELL', 'DNR', 'XRAY', 'DVN', 'DV', 'DO', 'DTV', 'DFS', 'DISCA', 'DLTR', 'D', 'RRD', 'DOV', 'DOW', 'DPS', 'DTE', 'DD', 'DUK', 'DNB', 'ETFC', 'EMN', 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EP', 'EA', 'EMC', 'EMR', 'ETR', 'EOG', 'EQT', 'EFX', 'EQR', 'EL', 'EXC', 'EXPE', 'EXPD', 'ESRX', 'XOM', 'FFIV', 'FDO', 'FAST', 'FII', 'FDX', 'FIS', 'FITB', 'FHN', 'FSLR', 'FE', 'FISV', 'FLIR', 'FLS', 'FLR', 'FMC', 'FTI', 'F', 'FRX', 'BEN', 'FCX', 'FTR', 'GME', 'GCI', 'GPS', 'GD', 'GE', 'GIS', 'GPC', 'GNW', 'GILD', 'GS', 'GR', 'GT', 'GOOG', 'GWW', 'HAL', 'HOG', 'HAR', 'HRS', 'HIG', 'HAS', 'HCP', 'HCN', 'HNZ', 'HP', 'HES', 'HPQ', 'HD', 'HON', 'HRL', 'HSP', 'HST', 'HCBK', 'HUM', 'HBAN', 'ITW', 'TEG', 'INTC', 'ICE', 'IBM', 'IFF', 'IGT', 'IP', 'IPG', 'INTU', 'ISRG', 'IVZ', 'IRM', 'XYL', 'JBL', 'JEC', 'CBE', 'JDSU', 'JNJ', 'JCI', 'JOY', 'JPM', 'JNPR', 'K', 'KEY', 'KMB', 'KIM', 'KLAC', 'KSS', 'KFT', 'KR', 'LLL', 'LH', 'LM', 'LEG', 'LEN', 'LUK', 'LXK', 'LIFE', 'LLY', 'LTD', 'LNC', 'LLTC', 'LMT', 'L', 'LO', 'LOW', 'LSI', 'MTB', 'M', 'MRO', 'MPC', 'MAR', 'MMC', 'MAS', 'ANR', 'MA', 'MAT', 'MKC', 'MCD', 'MHP', 'MCK', 'MJN', 'MWV', 'MHS', 'MDT', 'MRK', 'MET', 'PCS', 'MCHP', 'MU', 'MSFT', 'MOLX', 'TAP', 'MON', 'MCO', 'MS', 'MOS', 'MMI', 'MSI', 'MUR', 'MYL', 'NBR', 'NDAQ', 'NOV', 'NTAP', 'NFLX', 'NWL', 'NFX', 'NEM', 'NWSA', 'NEE', 'NKE', 'NI', 'NE', 'NBL', 'JWN', 'NSC', 'NTRS', 'NOC', 'NU', 'CMG', 'NVLS', 'NRG', 'NUE', 'NVDA', 'NYX', 'ORLY', 'OXY', 'OMC', 'OKE', 'ORCL', 'OI', 'PCAR', 'IR', 'PLL', 'PH', 'PDCO', 'PAYX', 'BTU', 'JCP', 'PBCT', 'POM', 'PEP', 'PKI', 'PRGO', 'PFE', 'PCG', 'PM', 'PNW', 'PXD', 'PBI', 'PCL', 'PNC', 'RL', 'PPG', 'PPL', 'PX', 'PCP', 'PCLN', 'PFG', 'PG', 'PGN', 'PGR', 'PLD', 'PRU', 'PEG', 'PSA', 'PHM', 'QEP', 'PWR', 'QCOM', 'DGX', 'RRC', 'RTN', 'RHT', 'RF', 'RSG', 'RAI', 'RHI', 'ROK', 'COL', 'ROP', 'ROST', 'RDC', 'R', 'SWY', 'SAI', 'CRM', 'SNDK', 'SLE', 'SCG', 'SLB', 'SNI', 'SEE', 'SHLD', 'SRE', 'SHW', 'SIAL', 'SPG', 'SLM', 'SJM', 'SNA', 'SO', 'LUV', 'SWN', 'SE', 'S', 'STJ', 'SWK', 'SPLS', 'SBUX', 'HOT', 'STT', 'SRCL', 'SYK', 'SUN', 'STI', 'SVU', 'SYMC', 'SYY', 'TROW', 'TGT', 'TEL', 'TE', 'THC', 'TDC', 'TER', 'TSO', 'TXN', 'TXT', 'HSY', 'TRV', 'TMO', 'TIF', 'TWX', 'TWC', 'TIE', 'TJX', 'TMK', 'TSS', 'TRIP', 'TSN', 'TYC', 'USB', 'UNP', 'UNH', 'UPS', 'X', 'UTX', 'UNM', 'URBN', 'VFC', 'VLO', 'VAR', 'VTR', 'VRSN', 'VZ', 'VIAB', 'V', 'VNO', 'VMC', 'WMT', 'WAG', 'DIS', 'WPO', 'WM', 'WAT', 'WPI', 'WLP', 'WFC', 'WDC', 'WU', 'WY', 'WHR', 'WFM', 'WMB', 'WIN', 'WEC', 'WPX', 'WYN', 'WYNN', 'XEL', 'XRX', 'XLNX', 'XL', 'YHOO', 'YUM', 'ZMH', 'ZION']


if __name__ == '__main__':
	main()
