
'''
This module manages and maintains data for RoboBuffett
'''


class financial_universe:
	'''Manage all financial information for all of the stocks. This will be the object that we pickle for serialization. For memory efficiency, it will not contain the full raw text of documents, but will contain methods by which they can be loaded into memeory.
	Perhaps we will want to include the word frequency counts since they will require less space. Will have to see whether it's practical.
	'''
	def __init__(self):
		self.companies  = {}
		self.industries = {}
		for document in our_SEC_Documents:
			company_quarter = make_company_quarter(document)
			if company_quarter.companyID not in self.companies:
				self.companies[companyID] = make_company(document) # Create a new company entry based on the document
			else:
				self.companies[companyID].add_quarter

			if document.industryID not in self.industries:
				self.industries[industryID] = industry(document) #Create a new industry entry
			else
				self.industries[industryID].add_new_document()


	def add_new_company(self, company):


class company:
	def __init__(self):
		company.industry = #Parse the document to get a SIC industry code
		company.timerange = #(startQuarter, endQuarter) showing when data begins and when data ends. e.g. (2002.75, 2012.25)
		company.quarters = {2002.25: company_quarter, ...}#dict of company_quarter objects indexed by the quarter

class industry:
	def __init__(self):
		industry.components = 

class quarter:
	def __init__(self, document):
		self.companyID = company.ID
		self.quarterID   = quarter #e.g. 2002.25
		self.industryID  = company.industry
		self.filingdate  = document.filingDate
		self.opening_price = get_opening_price(company, filingdate)
 # Pull information from the document to populate the 

class document:
	def __init__(self, docpath, doctype):
		'''Populate the following'''
		self.type = doctype
		self.properties = {}
		try:
			self.file = open(docpath, 'r')
		except IOError:
			print "Bad file path ", docpath
			return 02


		if document.type in ('10-Q', '10-K'):
			document.parse_quarterly_filing()
		else:
			print "Document not supported: %s type %s" % (docpath, doctype)

	def parse_quarterly_filing(self):
		property_info = ( 
		  #DictionaryName,    FilingText,                          isNumber
		 ('DocType',         'CONFORMED SUBMISSION TYPE:',          False),
		 ('ReportingPeriod', 'CONFORMED PERIOD OF REPORT:',         True ),
		 ('FilingDate',      'FILED AS OF DATE:',                   True ),
	 	 ('CompanyName',     'COMPANY CONFORMED NAME:',             False),
		 ('CIK',             'CENTRAL INDEX KEY',                   True ),
		 ('SIC',             'STANDARD INDUSTRIAL CLASSIFICATION:', True ),
		 ('IRS_Num',         'IRS NUMBER:',                         True ),
		 ('FY_End',          'FISCAL YEAR END:',                    True ),
		 ('SEC_FileNo',      'SEC FILE NUMBER:',                    False))
		# Defines the properties to seek in the header of the filing, and names to assign them to in the self.properties dictionary. I hope Python doesn't waste time re-creating this tuple every time parse_quarterly_filing is called.
		i = 0
		'Process the file line by line to get header info'
		for line in self.file:
			line = line.strip()
			if self.grab_property(line, *property_info[i]):
				i += 1
				if i = len(property_info):
					break

		'Now grab the entire document and process it to make a wordfreq'
		text = self.file.read.split()
		

		document.companyID = # Ref to Company (unique references)
		document.central_index_key =
		document.irs_number =
		document.industryID = #SIC code pulled from the document
		document.filingDate = 
		document.quarter = 
		document.wordfreq = #dict of word frequences
		document.wordcount = 

	def grab_property(self, line, propertyname, propertytag, isInt=False,):
		if line.startswith(propertytag):
			content = line.partition(propertytag)[2].strip()
			if isInt: content = int(content)
			if propertyname != '':
				self.properties[propertyname] = content
			return content