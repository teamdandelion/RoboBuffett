#!/usr/bin/env python

from collections import defaultdict


def main():


	lst = open('stocks_CIK.txt', 'r').read().split('\n')[:-1]

	''' Get rid of repeat CIK's : Find out a way to deal with them later'''
	remove_repeats = []
	for s in lst:
		remove_repeats += [k for k in lst if s.split('\t')[3]==s.split('\t')[3]]
	for r in remove_repeats:
		try: lst.remove(r)
		except: pass

	''' Properly parse stocks_CIK '''

	collector = defaultdict(list)
	for s in lst:
		l = s.split('\t')
		ticker = l[0] # obtain ticker symbol
		name   = l[1] # obtain company name
		flag   = int(l[2]) # CIK flag
		cik    = l[3]
		if flag   ==  -1:
			pass
		elif flag == 100:
			collector[(flag,1)].append((ticker,cik,name))
		elif (flag < 100) | (flag > -1):
			# If only one CIK
			if len(cik) == 10:
				collector[(flag,1)].append((ticker,cik,name))
			else:
				cik_eval = eval(cik)
				collector[(flag,len(cik_eval))].append((ticker,cik,name))
		else:
			print 'Encountered unexpected line, quit'
			exit()

	# Write good ticker, CIK pairs in here
	#writer = open('good_CIK.txt', 'w')
	#writer.write(ticker+'\t'+cik+'\n') # write pair to file
	#writer.close()

	d = dict(collector)

	k = d.keys()
	for i in k:
		if i[1] == 1:
			print i, len(collector[i])

		if i[0] == 100:
			print i, len(collector[i])

		if i[1] == 2:
			print i, len(collector[i])

		if i[1] == 3:
			print i, len(collector[i])

	with open('validated_CIK.txt','wb') as f:
		for k,v in d.iteritems():
			if (k[0] == 100) | (k[1] == 1):
				for i in v:
					f.write(i[0]+'\t'+i[1]+'\t'+i[2]+'\n')

	ones_list = []
	for k,v in d.iteritems():
		if (k[0] == 2) & (k[1] == 1):
			for i in v:
				ones_list.append([i[0],i[1],i[2]])

	matchcounter = 0
	for i in [i[1] for i in ones_list]:
		matchups = [(k[0],k[2]) for k in ones_list if k[1] == i]
		if len(matchups) > 1:
			print matchups
			matchcounter += 1

	print matchcounter


if __name__ == '__main__':
	main()
