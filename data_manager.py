
'''
This module manages and maintains data for RoboBuffett
'''


class financial_universe:
	'''Manage all financial information for all of the stocks. This will be the object that we pickle for serialization. For memory efficiency, it will not contain the full raw text of documents, but will contain methods by which they can be loaded into memeory.
	Perhaps we will want to include the word frequency counts since they will require less space. Will have to see whether it's practical.
	'''
	def __init__(self):
		self.firms  = {}
		self.industries = {}
		for document in ourSECDocuments:
			if document.firmID not in self.firms:
				self.firms[firmID] = firm(document) # Create a new company entry based on the document
				if document.industryID not in self.industries:


			else:
				self.firms[firmID].add_new_document(document)


	def add_new_company(self, company):


class company:
	def __init__(self):
		company.industry = #Parse the document to get a SIC industry code
		company.duration = #(startQuarter, endQuarter) showing when data begins and when data ends
		company.quarters = {2002.25: company_quarter, ...}#dict of company_quarter objects indexed by the quarter

class industry:
	def __init__(self):
		industry.components = 


class document:
	def __init__(self):
		'''Populate the following'''
		document.company = # Ref to Company (unique references)
		document.industryID = #SIC code pulled from the document
		document.filingDate = 
		document.quarter = 
		document.wordfreq = #dict of word frequences
		document.wordcount = 


class company_quarter: 
	'''
	Maintains information pertaining to 1 company at a specific moment of time... corresponds closely to the document class, but won't contain the text of the document for space efficiency. So financial_universe will store company_quarters, and each company_quarter will have a reference to the location of the document.
	'''
	def __init__(self, company, quarter):
		self.companyID = company.ID
		self.quarter   = quarter
		self.industry  = company.industry
		self.filingdate  = company.get_filingdate(quarter)
		self.opening_price = get_opening_price(company, filingdate)






def threshold_classification(companyID, quarter, duration)