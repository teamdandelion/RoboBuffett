#!/usr/bin/env python
'''
This module manages and maintains data for RoboBuffett
'''
import string
import os
import sys
from datetime import date, timedelta
import logging
from pdb import set_trace as debug
try:
	import cPickle as pickle
except:
	import pickle

class Financial_Universe:
	'''Manage all financial information for all of the stocks. This will be the object that we pickle for serialization. For memory efficiency, it will not contain the full raw text of documents, but will contain methods by which they can be loaded into memeory.
	Perhaps we will want to include the word frequency counts since they will require less space. Will have to see whether it's practical.
	'''
	def __init__(self, data_dir):
		self.companies  = {}
		self.industries = {}
		self.documents  = []
		for doc_path in os.listdir(data_dir):
			if doc_path[0] == ".": continue
			newdoc = Document(data_dir + doc_path, 'SEC_Quarterly')
			self.documents.append(newdoc)
			CIK = newdoc.CIK
			if CIK not in self.companies:
				self.companies[CIK] = Company(newdoc) # Create a new company entry based on the document
			else:
				self.companies[CIK].add_document(newdoc)

		for CIK, company in self.companies.iteritems():
			if CIK not in self.industries:
				self.industries[CIK] = Industry(CIK, company)
			else:
				self.industries[CIK].add_company(CIK, company)
		self.get_counts()


	def get_counts(self):
		sum = 0
		for doc in self.documents:
			sum += doc.word_count
		self.word_count = sum
		self.doc_count = len(self.documents)
		self.co_count = len(self.companies)
		self.indy_count = len(self.industries)


class Company:
	def __init__(self, document):
		self.CIK = document.CIK
		self.SIC = document.SIC
		self.documents = [(document.date, document)]
		self.name = document.cname

	def add_document(self, document):
		self.documents.append((document.date, document))
		if document.cname != company.name:
			print "Name discrepancy: %s, %s" % (company.name, document.cname)
			logging.debug("Name discrepancy: %s, %s" % (company.name, document.cname))
		if document.SIC != company.SIC:
			print "SIC discrepancy: %d %d" % (company.SIC, document.SIC)
			logging.debug("SIC discrepancy: %d %d" % (company.SIC, document.SIC))

class Industry:
	def __init__(self, CIK, company):
		self.SIC = company.SIC
		self.components = {CIK: company}
		self.n_componenets = 1
	
	def add_company(self, CIK, company):
		if CIK not in self.components:
			self.components[CIK] = company
			self.n_components += 1

# class Quarter:
# 	def __init__(self, document):
# 		self.companyID = company.ID
# 		self.quarterID   = quarter #e.g. 2002.25
# 		self.industryID  = company.industry
# 		self.filingdate  = document.filingDate
# 		self.opening_price = get_opening_price(company, filingdate)
#  # Pull information from the document to populate the 

class Document:
	def __init__(self, docpath, doctype):
		'''Populate the following'''
		self.path = docpath
		self.properties = {}
		self.word_freq = {}
		self.word_count = {}
		try:
			self.docfile = open(docpath, 'r')
		except IOError:
			print "Bad file path ", docpath
			logging.warning('Bad doc path: %s' % docpath)
			return 


		if doctype == 'SEC_Quarterly':
			self.parse_quarterly_filing()
		else:
			print "Document not supported: %s type %s" % (docpath, doctype)
			logging.warning('Unsupported doc %s type %s' % (docpath, doctype))

		self.docfile.close()
		del self.docfile


	def parse_quarterly_filing(self):
		'Define the properties we want to grab from the filing'
		property_info = ( 
		  #DictionaryName,    FilingText,                          isNumber
		 ('DocType',         'CONFORMED SUBMISSION TYPE:',          False),
		 ('ReportingPeriod', 'CONFORMED PERIOD OF REPORT:',         False),
		 ('FilingDate',      'FILED AS OF DATE:',                   False),
	 	 ('CompanyName',     'COMPANY CONFORMED NAME:',             False),
		 ('CIK',             'CENTRAL INDEX KEY:',                  True ),
		 ('SIC',             'STANDARD INDUSTRIAL CLASSIFICATION:', True ),
		 ('IRS_Num',         'IRS NUMBER:',                         True ),
		 ('FY_End',          'FISCAL YEAR END:',                    True ),
		 ('SEC_FileNo',      'SEC FILE NUMBER:',                    False))
		# Defines the properties to seek in the header of the filing, and names to assign them to in the self.properties dictionary. I hope Python doesn't waste time re-creating this tuple every time parse_quarterly_filing is called.
		# The last condition 'Item 1. B' triggers when we have parsed all the header info and are into the actual document. Since the dictionaryName is '' it won't store anything, but it returns a nonzero value so that the loop will break

		partition_text = 'PART I'
		text = self.docfile.read().partition(partition_text)
		# Currently I partition it into Header and Body by seperating at the first instance of the text 'PART I'. I consider this a placeholder
		if text[1] != partition_text:
			print "Warning: Unable to partition %s" % (self.path)
			logging.warning("ERROR: Unable to partition %s" % (self.path))
			return
		header = text[0].split("\n") #Consider mapping .strip for efficiency
		text = text[2]

		'Process the header line by line'
		i = 0
		for line in header:
			line = line.strip()
			if self.grab_property(line, *property_info[i]):
				i += 1
				if i == len(property_info):
					break
		if i != len(property_info):
			print "Found %d of %d fields for %s" % (i, len(property_info), self.path)
			logging.warning("Found %d of %d fields for %s" % (i, len(property_info), self.path))
		self.convert_property_to_date('ReportingPeriod')
		self.convert_property_to_date('FilingDate')

		self.date  = self.properties['FilingDate']
		self.type  = self.properties['DocType']
		self.CIK   = self.properties['CIK']
		self.SIC   = self.properties['SIC']
		self.cname = self.properties['CompanyName']

		'Now grab the entire document and process it to make a word_freq'
		text = text.translate(None, (string.punctuation + string.digits))
		text = text.lower().split()
		# Reads all words left in the file, removes all punctuation or numbers, converts to lowercase
		# Possible improvements: Strip tables, formatting (e.g. <PAGE>, - 2 -)
		self.word_count = len(text)
		for word in text:
			try: 
				self.word_freq[word] += 1
			except KeyError:
				self.word_freq[word] = 1
		# This try, except method may be somewhat more efficient than if-then branching for unigram processing. For n-grams, perhaps better to use if-then.

	def grab_property(self, line, propertyname, propertytag, isInt=False):
		if line.startswith(propertytag):
			content = line.partition(propertytag)[2].strip()
			if isInt: 
				try:
					content = int(content)
				except ValueError:
					logging.debug('''ValueError occured converting "%s" to int in line:\n%s . Forcing conversion.''' % (content, line))
					try: 
						content = int(content.translate(None, string.punctuation + string.ascii_letters + string.whitespace))
					except ValueError as e:
						logging.error('Unable to force-convert ' + str(e))
			if propertyname != '':
				self.properties[propertyname] = content
			return content
	
	def convert_property_to_date(self, propertyname):
		prop = self.properties[propertyname]
		yyyy = int(prop[0:4])
		mm   = int(prop[4:6])
		dd   = int(prop[6:8])
		self.properties[propertyname] = date(yyyy, mm, dd)


if __name__ == "__main__":
	if len(sys.argv) == 1:
		data_dir = "./Data/"
	else:
		data_dir = argv[1]

	with open('./data_manager.log', 'w') as cleanlog:
		pass

	logging.basicConfig(filename='data_manager.log', level=logging.DEBUG)
	universe = Financial_Universe(data_dir)

	print "Statistics: %d documents, %d companies %d industries %d words" % (universe.doc_count, universe.co_count, universe.indy_count, universe.word_count)
	logging.info("Statistics: %d documents, %d companies %d industries %d words" % (universe.doc_count, universe.co_count, universe.indy_count, universe.word_count))
	with open('./universe.dat', 'w') as f:
		pickle.dump(universe, f, 2)

