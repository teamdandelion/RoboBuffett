#!/usr/bin/env python

import os, sys, logging
from parser.py import DocError, parse_quarterly_filing
import stock


class Manager(object):
    def __init__(self, RB_Dir):
        self.industries = {}
        self.good_CIKs = stock.good_CIKs()
        self.active_companies = {}
        self.RB_dir = RB_dir
        os.chdir(RB_Dir)
        ensure('Data/')
        ensure('Data/Pickles/')
        ensure('Data/Active/')
        ensure('Data/Inactive/')
        ensure('Data/Unprocessed/')
        ensure('Data/Preprocessed/')
        ensure('Data/Processed/')
        ensure('Data/Exceptions/')

    def organize_documents(self):


    def preprocess(self):
        os.chdir('Data/Unprocessed')
        for docpath in os.listdir('.'):
            try:
                (header, filers) = parse_quarterly_header(docpath)
                date     = header['FilingDate']
                doctype  = header['DocType']
                for CIK in filers.iterkeys():
                    docname = CIK + '_' + date + '_' + doctype
                    if CIK in self.good_CIKs:
                        SIC = filers[CIK]['SIC']
                        comp = self.load_company(CIK, SIC)
                        comp.properties(filers[CIK])
                        comp.add_document(date, doctype, wordcount)
                        os.link(docpath, self.RB_Dir + '/Active/'   + docname)
                    else:
                        os.link(docpath, self.RB_Dir + '/Inactive/' + docname)
                os.rename(docpath, self.RB_Dir + '/Processed/'  + docpath)
            except:
                os.rename(docpath, self.RB_Dir + '/Exceptions/' + docpath)


    def load_company(self, CIK, SIC):
        # Look for the company in:
            # 1. The active list
            # 2. The pickles directory
            # 3. Make a new company
        # If #2, then add to active list. If #3, then add to active list and add SIC to industries.
        if CIK in self.active_companies:
            company = self.active_companies[CIK]
        elif (CIK+'.dat') in os.listdir(self.RB_dir + 'Data/Pickles'):
            with open(self.RB_dir + 'Data/Pickles/' + CIK + '.dat') as f:
                company = pickle.load(f)
            self.active_companies[CIK] = company

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

    def add_document(self, (wordcount, numwords)):

def ensure(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)