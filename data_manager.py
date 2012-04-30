
'''
This module manages and maintains data for 
'''


class financial_universe:
	def __init__(self):
		companies  = []
		industries = []
		for document in ourSECDocuments:
			if document.company not in companies:
				companies.append(document.company) # Need to have unique company references, use a companyID system
				if company.industry not in 

	def add_new_company(self, company)


class company_quarter: 
	'''

	'''
	def __init__(self, company, quarter):
		self.companyID = company.ID
		self.quarter   = quarter
		self.industry  = company.industry
		self.filingdate  = company.get_filingdate(quarter)
		self.opening_price = get_opening_price(company, filingdate)

	def threshold_classification(self, thresholds, duration):




class company:
	def __init__(self):
		company.industry = #Parse the document to get a SIC industry code

class industry:
	def __init__(self):
		industry.components = 




def threshold_classification(companyID, quarter, duration)