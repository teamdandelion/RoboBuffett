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
		self.doc_count  = len(self.documents)
		self.co_count   = len(self.companies)
		self.indy_count = len(self.industries)

	def generate_word_index(self, threshold):
		# Threshold in (0, 1)
		dict_index = {}
		threshold *= self.doc_count
		for document in self.documents:
			for word in document.word_freq.iterkeys():
				try: 
					dictindex[word] += 1
				except KeyError:
					dictindex[word]  = 1
		self.index_list = []
		for word, val in dictindex.iteritems():
			if val > threshold:
				self.index_list.append(word)
		del dictindex
		self.index_list.sort()
		self.index_dict = {}
		for i in xrange(len(self.index_list)):
			self.index_dict[index_list[i]] = i


class Company:
	def __init__(self, document):
		self.CIK = [document.CIK]
		self.SIC = document.SIC]
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

class Document:
	def __init__(self, docpath, doctype):
		'''Populate the following'''
		self.path = docpath
		self.properties = {}
		self.word_freq  = {}
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
		for line in header:
			line = line.strip()
		self.convert_property_to_date('ReportingPeriod')
		self.convert_property_to_date('FilingDate')
		self.date  = self.properties['FilingDate']
		self.type  = self.properties['DocType']
		self.CIK   = self.properties['CIK']
		self.SIC   = self.properties['SIC']
		self.cname = self.properties['CompanyName']

		# Possible improvements: Strip tables, formatting (e.g. <PAGE>, - 2 -)
		self.word_count = len(text)
		for word in text:
			try: 
				self.word_freq[word] += 1
			except KeyError:
				self.word_freq[word] = 1

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

