
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
	def __init__(self):
		'''Populate the following'''
		document.company = # Ref to Company (unique references)
		document.industryID = #SIC code pulled from the document
		document.filingDate = 
		document.quarter = 
		document.wordfreq = #dict of word frequences
		document.wordcount = 
