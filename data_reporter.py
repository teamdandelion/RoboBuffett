#!/usr/bin/env python
import os
import os.path
from os.path import isdir
import random
datadir = '/Volumes/Conduit/RBData'
years = map(str,range(1999,2012))
qtrs = ['QTR1','QTR2','QTR3','QTR4']


bad_years = []
bad_quarters = []

def djoin(dir1, dir2=""):
    return datadir + '/' + dir1 + '/' + dir2

def missing_linebreaks(filee):
    if os.path.getsize(filee) > 0 and os.path.isfile(filee):
        with open(filee, 'r') as f:
            i = 0
            for line in f:
                i += 1
                if i > 2:
                    return False
        print filee
        return True
    return False

for year in years:
    if not isdir(djoin(year)):
        print "!Year {} not found".format(year)
        bad_years.append(year)
        continue
    print "----"
    for qtr in qtrs:
        dirr = djoin(year,qtr)
        if not isdir(dirr):
            print "!Quarter {} {} not found".format(qtr,year)
            bad_quarters.append((qtr,year))
            continue

        os.chdir(dirr)
        files = len(os.listdir('.'))
        size = float(sum([os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f)])) / (1024**3)
        if files > 0:
            avg = size / files * (1024**2)
        else:
            avg = 0

        rsample = random.sample(os.listdir('.'),min(20,files))
        missing_lb = any(map(missing_linebreaks, rsample))

        print "Quarter {} {}: {:6d} files, {:1.2f}GB size, {:4.0f}kB avg size".format(qtr, year, files, size, avg)
        if missing_lb:
            print "Quarter {} {}: Missing linebreaks!".format(qtr,year)
            print zip(rsample,map(missing_linebreaks, rsample))





