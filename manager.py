#!/usr/bin/env python

import os, sys, logging, string
from parser import DocError, parse_quarterly_filing
from pdb import set_trace as debug
from os.path import basename
#import stock

def main():
    DataDir = os.path.expanduser('~/Documents/Code/RoboBuffett/Data/')
    manager = Manager(DataDir)
    manager.preprocess()


class Manager(object):
    def __init__(self, DataDir):
        self.industries = {}
        self.active_companies = {}
        self.DataDir = DataDir
        os.chdir(DataDir)
        ensure('Pickles/')
        ensure('Active/')
        ensure('Inactive/')
        ensure('Unprocessed/')
        ensure('Preprocessed/')
        ensure('Processed/')
        ensure('Exceptions/')

    def organize_documents(self):
        pass


    def preprocess(self):
        os.chdir(self.DataDir + 'Unprocessed/')
        for docpath in recursive_file_gen('.'):
            if basename(docpath)[0] in ('.', '_'): continue
            try:
                (header, filers, _) = parse_quarterly_filing(docpath)
                date     = header['FilingDate']
                doctype  = header['DocType']
                for CIK in filers.iterkeys():
                    docname = CIK + '_' + date '.txt'
                    ensure(self.DataDir + 'Preprocessed/' + CIK)
                    safelink(docpath, self.DataDir + 'Preprocessed/' + CIK + '/' + docname)
            except DocError as e:
                print e
                safelink(docpath, self.DataDir + 'Exceptions/' + basename(docpath))

    def active_dir(self, pathname):
        os.chdir(self.DataDir + pathname)

    def process(self):
        os.chdir(self.DataDir + 'Preprocessed')


                    # if CIK in self.good_CIKs:
                    #     SIC = filers[CIK]['SIC']
                    #     comp = self.load_company(CIK, SIC)
                    #     comp.properties(filers[CIK])
                    #     comp.add_document(date, doctype, wordcount)
                    #     os.link(docpath, self.DataDir + '/Active/'   + docname)
                    # else:
                    #     os.link(docpath, self.DataDir + '/Inactive/' + docname)


    def load_company(self, CIK, SIC):
        # Look for the company in:
            # 1. The pickles directory
            # 2. Make a new company
        # If #2, then add to active list. If #3, then add to active list and add SIC to industries.
        if (CIK+'.dat') in os.listdir(self.DataDir + 'Pickles'):
            with open(self.DataDir + 'Pickles/' + CIK + '.dat') as f:
                company = pickle.load(f)
        else:
            company = Company(CIK, SIC)
            self.active_companies[CIK] = company
            try: 
                self.industries[SIC].append(company)
            except KeyError:
                self.industries[SIC] = company



class Company(object):
    def __init__(self, CIK, SIC):
        self.CIK = CIK
        self.industry = SIC

    def properties(self, propdict):
        # If company has no properties, then add them. If not, check for discrepancies
        pass

    def add_document(self, (wordcount, numwords)):
        pass

def recursive_file_gen(mydir):
    for root, dirs, files in os.walk(mydir):
        for file in files:
            yield os.path.join(root, file)

def ensure(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def safelink(source, dest):
    try: 
        os.link(source, dest)
    except OSError:
        pass

def force_to_int(val):
    try:
        converted = int(val)
    except ValueError:
        to_remove = string.punctuation + string.letters + string.whitespace
        val = val.translate(None, (to_remove))
        converted = int(val)
    return converted


if __name__ == "__main__":
    main()