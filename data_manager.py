
'''
This module manages and maintains data for RoboBuffett
'''
import string
import os
from pdb import set_trace as debug

# class financial_universe:
# 	'''Manage all financial information for all of the stocks. This will be the object that we pickle for serialization. For memory efficiency, it will not contain the full raw text of documents, but will contain methods by which they can be loaded into memeory.
# 	Perhaps we will want to include the word frequency counts since they will require less space. Will have to see whether it's practical.
# 	'''
# 	def __init__(self):
# 		self.companies  = {}
# 		self.industries = {}
# 		for document in our_SEC_Documents:
# 			company_quarter = make_company_quarter(document)
# 			if company_quarter.companyID not in self.companies:
# 				self.companies[companyID] = make_company(document) # Create a new company entry based on the document
# 			else:
# 				self.companies[companyID].add_quarter

# 			if document.industryID not in self.industries:
# 				self.industries[industryID] = industry(document) #Create a new industry entry
# 			else
# 				self.industries[industryID].add_new_document()


# 	def add_new_company(self, company):


# class company:
# 	def __init__(self):
# 		company.industry = #Parse the document to get a SIC industry code
# 		company.timerange = #(startQuarter, endQuarter) showing when data begins and when data ends. e.g. (2002.75, 2012.25)
# 		company.quarters = {2002.25: company_quarter, ...}#dict of company_quarter objects indexed by the quarter

# class industry:
# 	def __init__(self):
# 		industry.components = 

# class quarter:
# 	def __init__(self, document):
# 		self.companyID = company.ID
# 		self.quarterID   = quarter #e.g. 2002.25
# 		self.industryID  = company.industry
# 		self.filingdate  = document.filingDate
# 		self.opening_price = get_opening_price(company, filingdate)
#  # Pull information from the document to populate the 

class document:
	def __init__(self, docpath, doctype):
		'''Populate the following'''
		self.path = docpath
		self.type = doctype
		self.properties = {}
		self.word_freq = {}
		self.word_count = {}
		try:
			self.file = open(docpath, 'r')
		except IOError:
			print "Bad file path ", docpath
			return 02


		if self.type in ('10-Q', '10-K'):
			self.parse_quarterly_filing()
		else:
			print "Document not supported: %s type %s" % (docpath, doctype)

		self.file.close()


	def parse_quarterly_filing(self):
		'Define the properties we want to grab from the filing'
		property_info = ( 
		  #DictionaryName,    FilingText,                          isNumber
		 ('DocType',         'CONFORMED SUBMISSION TYPE:',          False),
		 ('ReportingPeriod', 'CONFORMED PERIOD OF REPORT:',         True ),
		 ('FilingDate',      'FILED AS OF DATE:',                   True ),
	 	 ('CompanyName',     'COMPANY CONFORMED NAME:',             False),
		 ('CIK',             'CENTRAL INDEX KEY:',                  True ),
		 ('SIC',             'STANDARD INDUSTRIAL CLASSIFICATION:', True ),
		 ('IRS_Num',         'IRS NUMBER:',                         True ),
		 ('FY_End',          'FISCAL YEAR END:',                    True ),
		 ('SEC_FileNo',      'SEC FILE NUMBER:',                    False))
		# Defines the properties to seek in the header of the filing, and names to assign them to in the self.properties dictionary. I hope Python doesn't waste time re-creating this tuple every time parse_quarterly_filing is called.
		# The last condition 'Item 1. B' triggers when we have parsed all the header info and are into the actual document. Since the dictionaryName is '' it won't store anything, but it returns a nonzero value so that the loop will break

		text = self.file.read().partition('ITEM 1. BUSINESS')
		if text[2] == '':
			print "ERROR: Bad partition %s %s" % (docpath, doctype)
			return 0
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
		print "Found %d of %d fields" % (i, len(property_info))

		if self.properties[DocType] != self.type:
			print "ERROR: Conflicting types for %s: %s reported %s discovered." % (self.path, self.type, self.properties[DocType])
		del self.properties[DocType]

		'Now grab the entire document and process it to make a wordfreq'
		debug()
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
					debug()
			if propertyname != '':
				self.properties[propertyname] = content
			return content