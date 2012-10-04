#!/usr/bin/env python

import os, sys, logging, string, time, math
from parser import ParseError, parse_quarterly_filing, build_word_count
from pdb import set_trace as debug
from os.path import basename
Path = os.path.join
try:
    import cPickle as pickle
except:
    import pickle
#import stock


def main():
# Todo: Implement better UI
    DataDir = os.path.expanduser('~/Documents/Code/RoboBuffett/Data/')
    logfile = DataDir + '../Logs/manager.log'
    touch(logfile)
    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    manager = load_manager(DataDir)
    #manager.preprocess()
    #manager.process()
    #save_manager(manager)
    #save_industry_dict(manager)
    pretty_dict(manager.industries)
    manager.print_stats()


def load_manager(DataDir):
    '''Load the manager from desk if it's available, or generate a new Manager instance if not'''
    try:
        with open(DataDir + 'Pickles/manager.dat', 'r') as f:
            return pickle.load(f)
    except IOError:
        return Manager(DataDir)

def save_manager(manager):
    '''Saves the manager to disk'''
    with open(manager.DataDir + 'Pickles/manager.dat', 'w') as f:
            pickle.dump(manager, f, 2)

def save_industry_dict(manager):
    '''Saves industry dict, useful for generating price indices'''
    with open(manager.DataDir + 'Pickles/industrydict.dat', 'w') as f:
        pickle.dump(manager.industries, f, 0)

class Manager(object):
    """Persistent object that manages the entire dataset
    Functionality overview:
    init         = Basic setup
    preprocess   = Vital step that organizes documents by CIK. Moves 
                   unparseable documents to 'Exceptions'
    process      = Process documents in Data/Preprocessed. Create company
                   entries containing parsed word counts. Moves documents
                   to 'Active' or 'Inactive'
    print_stats  = Print a bunch of statistics about the manager
    
    Terminology:
    CIK: Central Index Key, used as unique identifiers for companies
    SIC: Standard Industrial Code, SEC's industry designators
    good CIK: a CIK for which we have stock price information
    active CIK: a CIK in the document dataset which is good
    inactive CIK: a CIK in the document dataset which isn't good
    processed documents: have been run thru the pre-processor
    exception documents: they didn't parse
    active documents: 'owned' by an active CIK
    inactive documents: not owned by an active CIK
    valid documents: union of active and inactive documents


    """
    def __init__(self, DataDir):
        ### Set up directory structure ###
        self.DataDir = DataDir
        os.chdir(DataDir)
        vital_dirs = ('Pickles/','Pickles/CIKs','Active/','Inactive/',
            'Unprocessed/','Preprocessed/','Processed/','Exceptions/')
        map(ensure, vital_dirs) # Make sure they all exist

        ### Mappings ###
        self.industries = {} # Mapping from SIC->[CIK]
        self.CIK_to_Ticker = dePickle('Pickles/CIK_Ticker.dat') 

        ### Sets ###
        self.good_CIKs     = set(self.CIK_to_Ticker.iterkeys()) 
        self.active_CIKs   = set() 
        self.CIK2date = {} # Map from active CIKs to documents (the dates)
        self.inactive_CIKs = set() 
        self.processed_docs = set() 
        # Original names of all documents processed by the manager.
        # Maintained to avoid double-counting documents. 
        self.valid_docs     = set() 
        
        # Invariant: len(processed) >= len(valid) - len(exception)
        # This is because for every processed document, the parser 
        # either fails and generates an exception, or succeeds and 
        # creates 1 or more valid documents corresponding to the 
        # number of valid filers (unique CIKs) found in the document.
        self.exception_docs = set() 
        self.active_docs    = set() 
        self.inactive_docs  = set() 


    def preprocess(self):
        """Preprocess the documents in Data/Unprocessed 
        Finds a doc's CIKs and creates hard links in the folder 
        Preprocessed/CIK. If a doc doesn't parse properly, it is 
        moved to Data/Exceptions instead. 
        The pre-processing step allows us to consider only one CIK 
        at a time during the processing step, for memory efficiency.
        """
        n_proc = 0
        n_valid = 0
        n_except = 0
        start = time.time()
        os.chdir(self.DataDir + 'Unprocessed/')
        for (docpath, docname) in recursive_file_gen('.'):
        # Returns (path, filename) tuples for all files in directory 
        # and subdirectories that don't begin with '.' or '_'
            if docname in self.processed_docs: continue
            self.processed_docs.add(docname) 
            n_proc += 1
            # Code assumes that docnames are unique
            try:
                (header, cik2filers, _) = parse_quarterly_filing(docpath)
                # Returns (but doesn't process) the raw text. 
                date     = header['FilingDate']
                doctype  = header['DocType']
                for CIK in cik2filers.iterkeys():
                    new_docname = CIK + '_' + date + '.txt'
                    ensure(self.DataDir + 'Preprocessed/' + CIK)
                    safelink(docpath, self.DataDir + 'Preprocessed/' + CIK + '/' + new_docname)
                    if new_docname in self.valid_docs:
                        print "Repeated doc: %s" % new_docname
                    self.valid_docs.add(new_docname)
                    n_valid += 1
                if n_valid != len(self.valid_docs):
                    pass#debug()

            except ParseError as e:
                self.exception_docs.add(docname)
                n_except += 1
                logging.warning(docname + ": " + str(e))
                safelink(docpath, self.DataDir + 'Exceptions/' + basename(docpath))


            # if n_proc > n_valid + n_except:
            #     print "Warning: proc %d, valid %d, except %d" % (n_proc, n_valid, n_except)
            # elif n_proc % 100 == 0:
            #     print "Proc %d, valid %d, except %d, combined %d" % (n_proc, n_valid, n_except, n_valid + n_except)
            #     if n_proc != len(self.processed_docs) or n_valid != len(self.valid_docs) or n_except != len(self.exception_docs):
            #         debug()

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
                if CIK not in self.CIK2date:
                    self.CIK2date[CIK] = []
                for filing in os.listdir(CIK):
                    filingpath = CIK + '/' + filing
                    (header, filers, rawtext) = parse_quarterly_filing(filingpath)
                    company.properties(filers)
                    date = header['FilingDate']
                    company.add_document(date, rawtext)
                    self.CIK2date[CIK].append(date)
                    self.active_docs.add(filing)
                    os.rename(filingpath, self.DataDir + 'Active/' + filingpath)
                self.save_company(company)
                SIC = company.SIC
                
                try: 
                    if CIK not in self.industries[SIC]:
                        self.industries[SIC].append(CIK)
                except KeyError:
                    self.industries[SIC] = [CIK]
                del company # Get it out of memory. Probably unnecessary

            else: # if CIK not in self.goodCIKs
                self.inactive_CIKs.add(CIK)
                ensure(self.DataDir + 'Inactive/' + CIK)
                for filing in os.listdir(CIK):
                    self.inactive_docs.add(filing)
                    os.rename(CIK +'/'+ filing, 
                        self.DataDir + 'Inactive/' + CIK +'/'+ filing)
            os.removedirs(CIK)
        end = time.time()
        print "Time elapsed in processing: %.1f" % (end-start)

    def gen_training_set(self, cutoff, skipyears):
        self.training_set = {}
        for CIK, dates in self.CIK2date:
            if random.random() > cutoff: continue
            datelist = []
            for date in dates:
                if date not in skipyears:
                    datelist.append(date)
            if datelist != []:
                self.training_set[CIK] = datelist






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

    def print_stats(self):
        good       = len(self.good_CIKs)
        active     = len(self.active_CIKs)
        inactive   = len(self.inactive_CIKs)
        sics       = len(self.industries.keys())
        proc       = len(self.processed_docs)
        valid      = len(self.valid_docs)
        exceptions = len(self.exception_docs)
        activeD    = len(self.active_docs)
        inactiveD  = len(self.inactive_docs)
        try:
            safeprint("%d good CIKs, %d active CIKs, %d inactive CIKs" % (good, active, inactive))
            safeprint("%.2f of observed CIKs are active, %.2f of good CIKs are active" % (active / float(active + inactive), active / float(good)))
            safeprint("%d SICs, average of %1.2f active CIKs per SIC" % (sics, active / float(sics)))
            safeprint("%d processed documents, %d valid, %d exceptions" % (proc, valid, exceptions))
            safeprint("Implied: %1.2f CIKs per document, %.2f exception rate" % (valid / float(proc - exceptions), exceptions / float(proc)))
            safeprint("%d active documents, %d inactive, %.2f activation rate" % (activeD, inactiveD, activeD / float(proc)))
        except ZeroDivisionError:
            safeprint("Please run the manager on some files before printing stats")

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


def proportional_set_intersection(sets, p):
    # Takes a list of sets: [Set1, Set2, Set3].
    # s = len(sets)
    # Returns a set containing every element which was in at least p proportion of the sets, i.e. there were at least s * p instances in the sets
    count = {}
    for sett in sets:
        for element in sett:
            try:
                count[element] += 1
            except KeyError:
                count[element]  = 1

    s = len(sets)
    n = math.floor(s * p)

    outset = set()
    for key,val in count.iteritems():
        if val > n:
            outset.add(key)




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

def safeprint(string):
    try:
        print string
    except:
        pass

def pretty_dict(output):
    lenlist = []
    for key, val in output.iteritems():
        lenlist.append((key,len(val)))
    lenlist = sorted(lenlist, key=lambda student: student[1])
    for (sic, i) in lenlist:
        print str(sic) + ('*' * i)

if __name__ == "__main__":
    main()