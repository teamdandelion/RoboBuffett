#!/usr/bin/env python
'''
This module manages and maintains data for RoboBuffett
'''
import os, sys, logging, string
from datetime import date, timedelta
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
			CIK = newdoc.CIK[0] # CIKs stored as a list since there may be several
			"""***TODO:***: Better system for handling CIKs, integrate with stock tickers"""

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
		"""Generates an index of commonly used words in the documents, so that the documents can be stored in compressed form. We can remove all instances of commonly used words from the dictionaries, and add a k-tuple of word counts, where k is the number of commonly used words. THRESHOLD determines what proportion of documents a word must be in for it to be included in the list.
		Creates self.index_list, an ordered list of words in the index. Creates self.index_dict which maps from element indicies back to the right word in the sequence. Sets self.indexed = 1."""
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
		self.indexed = 1

class Company:
	def __init__(self, document):
		self.CIK = document.CIK
		self.SIC = document.SIC
		self.documents = [(document.date, document)]
		self.name = document.cname

	def __repr__(self):
		return "<COMPANY>" + self.name[0] # Currently names are stored as a list as there may be multiple. Not a super satisfactory solution

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

	def __repr__(self):
		return "<INDUSTRY>" + str(self.SIC[0])
	
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
		del self.docfile # Delete file references so Pickle won't complain

	def __repr__(self):
		return "<DOCUMENT>" + self.path


	def parse_quarterly_filing(self):
		"""Parse a quarterly filing. Makes a dictionary in self.properties containing all of the attributes pulled from the quarterly filing. Makes a word-frequency too."""
		# The last condition 'Item 1. B' triggers when we have parsed all the header info and are into the actual document. Since the dictionaryName is '' it won't store anything, but it returns a nonzero value so that the loop will break

		logging.info("Parsing quarterly filing %s" % self.path)
		partition_text = 'PART I'
		text = self.docfile.read().partition(partition_text)
		# Currently I partition it into Header and Body by seperating at the first instance of the text 'PART I'. I consider this a placeholder
		if text[1] != partition_text:
			print "Warning: Unable to partition %s" % self.path
			logging.warning("ERROR: Unable to partition document.")
			return
		header = text[0].split("\n") #Consider mapping .strip for efficiency
		text = text[2]
		self.parse_quarterly_header(header)
		self.build_word_freq(text)

	def parse_quarterly_header(self, header):
		property_info = ( 
		  #DictionaryName,    FilingText,                   int   list
		 ('DocType',         'CONFORMED SUBMISSION TYPE:',   0,     0),
		 ('ReportingPeriod', 'CONFORMED PERIOD OF REPORT:',  0,     0),
		 ('FilingDate',      'FILED AS OF DATE:',            0,     0),
	 	 ('CompanyName',     'COMPANY CONFORMED NAME:',      0,     1),
		 ('CIK',             'CENTRAL INDEX KEY:',           1,     1),
		 ('SIC',      'STANDARD INDUSTRIAL CLASSIFICATION:', 1,     1),
		 ('IRS_Num',         'IRS NUMBER:',                  1,     1),
		 ('FY_End',          'FISCAL YEAR END:',             1,     1),
		 ('SEC_FileNo',      'SEC FILE NUMBER:',             1,     1))
		# Defines the properties to seek in the header of the filing, and names to assign them to in the self.properties dictionary. I hope Python doesn't waste time re-creating this tuple every time parse_quarterly_filing is called.
		for line in header:
			line = line.strip()
			for property_tuple in property_info:
				self.grab_property(line, *property_tuple)

		if len(self.properties) < len(property_info):
			msg = "Found %d of %d fields" % (len(self.properties), len(property_info))
			logging.warning(msg)
		
		self.convert_property_to_date('ReportingPeriod')
		self.convert_property_to_date('FilingDate')
		self.date  = self.properties['FilingDate']
		self.type  = self.properties['DocType']
		self.CIK   = self.properties['CIK'] # A list
		self.SIC   = self.properties['SIC'] # A list
		self.cname = self.properties['CompanyName'] # A list

	def build_word_freq(self, text):
		to_remove = string.punctuation + string.digits
		text = text.translate(None, (to_remove))
		# Removes all punctuation and digits
		text = text.lower()
		text = text.split()
		# Splits the text into a list of lowercase words
		# Possible improvements: Strip tables, formatting (e.g. <PAGE>, - 2 -)
		self.word_count = len(text)
		for word in text:
			try: 
				self.word_freq[word] += 1
			except KeyError:
				self.word_freq[word] = 1
		# This try/except method may be somewhat more efficient than if-then branching for unigram processing. For n-grams, perhaps better to use if-then.

	def grab_property(self, line, name, identifier, isInt=0, isList=0):
		"""Checks LINE for IDENTIFIER. If IDENTIFIER is found in the line, then the text immediately after IDENTIFIER is saved in self.properties[PROPNAME]. If the isInt flag is set, then the content is converted to an integer value. If it doesn't convert to int cleanly, then non-digits characters are stripped, it's force converted, and a note is made in the log. In text mode, leading or trailing whitespace around the content is also removed. grab_property returns the content that it stores. If PROPNAME is "" then no value is stored, but the content is still returned."""
		if line.startswith(identifier):
			content = line.partition(identifier)[2].strip()
			# Take the content after the identifier, and strip whitespace
			props = self.properties
			if isInt: 
				try:
					content = int(content)
				except ValueError:
					logging.debug('''ValueError occured converting "%s" to int in line:\n%s . Forcing conversion.''' % (content, line))
					try: 
						to_remove = string.punctuation + string.ascii_letters + string.whitespace
						content = int(content.translate(None, to_remove))
					except ValueError as e:
						logging.error('Unable to force-convert ' + str(e))
			if name != '': 
			# If propname is the empty string, nothing is stored
				if isList:
					if name in props: # Append to existing list
						props[name].append(content)
					else: # Start a new list
						props[name] = [content]
				else: # Just store a value
					props[name] = content
			return content
	
	def convert_property_to_date(self, propname):
		prop = self.properties[propname]
		yyyy = int(prop[0:4])
		mm   = int(prop[4:6])
		dd   = int(prop[6:8])
		self.properties[propname] = date(yyyy, mm, dd)

def main():
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
	debug()

if __name__ == "__main__":
	main()


