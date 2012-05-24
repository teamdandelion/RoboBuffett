#!/usr/bin/env python

import os, sys, logging, string, time
from parser import DocError, parse_quarterly_filing, build_word_count
from pdb import set_trace as debug
from os.path import basename
Path = os.path.join
try:
    import cPickle as pickle
except:
    import pickle
#import stock

def main():
    DataDir = os.path.expanduser('~/Documents/Code/RoboBuffett/Data/')
    logfile = DataDir + '../Logs/manager.log'
    touch(logfile)
    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    manager = load_manager(DataDir)
    manager.preprocess()
    manager.process()
    save_manager(manager)
    save_industry_dict(manager)
    manager.print_stats()
    

def load_manager(DataDir):
    try:
        with open(DataDir + 'Pickles/manager.dat', 'r') as f:
            return pickle.load(f)
    except IOError:
        return Manager(DataDir)

def save_manager(manager):
    with open(manager.DataDir + 'Pickles/manager.dat', 'w') as f:
            pickle.dump(manager, f, 2)

def save_industry_dict(manager):
    with open(manager.DataDir + 'Pickles/industrydict.dat', 'w') as f:
        pickle.dump(manager.industries, f, 0)

class Manager(object):
    def __init__(self, DataDir):
        os.chdir(DataDir)
        ensure('Pickles/')
        ensure('Pickles/CIKs')
        ensure('Active/')
        ensure('Inactive/')
        ensure('Unprocessed/')
        ensure('Preprocessed/')
        ensure('Processed/')
        ensure('Exceptions/')
        self.industries = {} # Mapping from SIC->CIK
        self.DataDir = DataDir
        self.CIK_to_Ticker = dePickle('Pickles/CIK_Ticker.dat') # Mapping from CIK -> Ticker
        self.good_CIKs     = set(self.CIK_to_Ticker.iterkeys()) # Set of all CIKs with assosc. tickers
        self.active_CIKs   = set() # Set of all CIKs found in dataset with all assosc. tickers. Represented in the 'Active' directory
        self.inactive_CIKs = set() # Set of all CIKs found in the dataset without assosc. tickers. Represented in the 'Inactive' directory
        self.processed_documents = set() # Set of all documents that have been processed by the manager.  
        self.valid_documents     = set() # Set of all documents that parsed properly
        self.exception_documents = set() # Set of all documents that failed to parse properly
        self.active_documents    = set() # Set of all valid documents with assosc. ticker
        self.inactive_documents  = set() # Set of all valid documents w/o assosc. ticker

    def print_stats(self):
        good       = len(self.good_CIKs)
        active     = len(self.active_CIKs)
        inactive   = len(self.inactive_CIKs)
        sics       = len(self.industries.keys())
        proc       = len(self.processed_documents)
        valid      = len(self.valid_documents)
        exceptions = len(self.exception_documents)
        activeD    = len(self.active_documents)
        inactiveD  = len(self.inactive_documents)
        try:
            print "%d good CIKs, %d active CIKs, %d inactive CIKs" % (good, active, inactive)
            print "%.2f of observed CIKs are active, %.2f of good CIKs are active" % (active / float(active + inactive), active / float(good))
            print "%d SICs, average of %1.2f active CIKs per SIC" % (sics, active / float(sics))
            print "%d processed documents, %d valid, %d exceptions" % (proc, valid, exceptions)
            print "Implied: %1.2f CIKs per document, %.2f exception rate" % (valid / float(proc - exceptions), exceptions / float(proc)) 
            print "%d active documents, %d inactive, %.2f activation rate" % (activeD, inactiveD, activeD / float(proc)) 
        except ZeroDivisionError:
            print "Please run the manager on some files before printing stats"

    def preprocess(self):
        start = time.time()
        os.chdir(self.DataDir + 'Unprocessed/')
        for (docpath, docname) in recursive_file_gen('.'):
        # Returns (path, filename) tuples for all files in directory and subdirectories that don't begin with '.' or '_'
            if docname in self.processed_documents: continue
            self.processed_documents.add(docname) # Assumes that docnames are unique
            try:
                (header, filers, _) = parse_quarterly_filing(docpath)
                date     = header['FilingDate']
                doctype  = header['DocType']
                for CIK in filers.iterkeys():
                    docname = CIK + '_' + date + '.txt'
                    ensure(self.DataDir + 'Preprocessed/' + CIK)
                    safelink(docpath, self.DataDir + 'Preprocessed/' + CIK + '/' + docname)
                    self.valid_documents.add(docname)
            except DocError as e:
                self.exception_documents.add(docname)
                logging.exception(e)
                safelink(docpath, self.DataDir + 'Exceptions/' + basename(docpath))
        end = time.time()
        print "Time elapsed in preprocessing: %.1f" % (end-start)

    def process(self):
        start = time.time()
        os.chdir(self.DataDir + 'Preprocessed')
        for CIK in os.listdir('.'):
            if CIK[0] == '.' or not os.path.isdir(CIK): pass

            if CIK in self.good_CIKs:
                self.active_CIKs.add(CIK)
                company = self.load_company(CIK)
                ensure(self.DataDir + 'Active/' + CIK)
                for filing in os.listdir(CIK):
                    filingpath = CIK + '/' + filing
                    (header, filers, rawtext) = parse_quarterly_filing(filingpath)
                    company.properties(filers)
                    date = header['FilingDate']
                    company.add_document(date, rawtext)
                    self.active_documents.add(filing)
                    os.rename(filingpath, self.DataDir + 'Active/' + filingpath)
                self.save_company(company)
                SIC = company.SIC
                
                try: 
                    if CIK not in self.industries[SIC]:
                        self.industries[SIC].append(CIK)
                except KeyError:
                    self.industries[SIC] = [CIK]
                del company # Get it out of memory. Probably unnecessary since the company name gets reassigned in next iteration of the loop for a good CIK and the garbage collector can spot that its reference count goes to 0.

            else: # if CIK not in self.goodCIKs
                self.inactive_CIKs.add(CIK)
                ensure(self.DataDir + 'Inactive/' + CIK)
                for filing in os.listdir(CIK):
                    self.inactive_documents.add(filing)
                    os.rename(CIK + '/' + filing, self.DataDir + 'Inactive/' + CIK + filing)
            os.removedirs(CIK)
        end = time.time()
        print "Time elapsed in processing: %.1f" % (end-start)


    def load_company(self, CIK):
        # Look for the company in:
            # 1. The pickles directory
            # 2. Make a new company
        # If #2, then add to active list. If #3, then add to active list and add SIC to industries.
        if os.path.exists(self.DataDir + 'Pickles/CIKs/' + CIK + '.dat'):
            with open(self.DataDir + 'Pickles/CIKs/' + CIK + '.dat', 'r') as f:
                company = pickle.load(f)
        else:
            company = Company(CIK)
        return company

    def save_company(self, company):
        with open(self.DataDir + 'Pickles/CIKs/' + company.CIK + '.dat', 'w') as f:
            pickle.dump(company, f, 2)


class Company(object):
    def __init__(self, CIK):
        self.CIK = CIK
        self.SIC = 0
        self.name = ''
        self.dates = []
        self.docs = {} # (count_dict, #words) tuples are indexed by filingdate

    def properties(self, filers):
        # If company has no properties, then add them. If not, check for discrepancies
        filerdict = filers[self.CIK]
        newSIC = filerdict['SIC']
        if self.SIC == 0:
            self.SIC = newSIC
        elif self.SIC != newSIC:
            logging.warning("Company switched SICs: CIK: %s orig SIC: %d new SIC: %d" % (self.CIK, self.SIC, newSIC))
        cname = filerdict['CompanyName']
        if self.name == '':
            self.name = cname
        elif self.name != cname:
            logging.warning("Company switched names: %s %s" % (self.name, cname))


    def add_document(self, filing_date, raw_text):
        self.dates.append(filing_date)
        self.docs[filing_date] = build_word_count(raw_text)


def recursive_file_gen(mydir):
    for root, dirs, files in os.walk(mydir):
        for file in files:
            if file[0] not in ('.', '_'):
                yield (os.path.join(root, file), file)

def ensure(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def touch(filepath):
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            pass

def safelink(source, dest):
    try: 
        os.link(source, dest)
    except OSError:
        pass

def dePickle(filestr):
    with open(filestr, 'r') as f:
        return pickle.load(f)


if __name__ == "__main__":
    main()