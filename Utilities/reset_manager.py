#!/usr/bin/env python

import os, shutil

def clean_all():
    DataDir = os.path.expanduser('~/Documents/Code/RoboBuffett/Data/')
    temp = DataDir + 'Temp/'
    ensure(temp)
    ensure(temp + 'Pickles/')
    to_delete = ('Preprocessed','Active','Inactive','Processed','Exceptions','Pickles/CIKs', 'Pickles/manager.dat')
    for item in to_delete:
        try:
            os.rename(DataDir + item, temp + item)
        except OSError as e:
            print str(e) +': ' + item
    print "Renamed, removing temp dir"
    shutil.rmtree(temp)

def ensure(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

if __name__ == "__main__":
    clean_all()