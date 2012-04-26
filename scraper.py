from ftplib import FTP
import os
import sys
import zipfile
import re

def connect_to_SEC(index):
    if index > 50:
        print "Maximum number of attempts exceeded. Try again later."
    else:
        try:
            return FTP('ftp.sec.gov')
        except EOFError:
            print "Connection refused on attempt {0}. Trying again...".format(index)
            return connect_to_SEC(index + 1)

ftp = connect_to_SEC(0)
ftp.login()

years = ['1993', 
         '1994', 
         '1995', 
         '1996', 
         '1997', 
         '1998', 
         '1999', 
         '2000', 
         '2001', 
         '2002', 
         '2003', 
         '2004', 
         '2005', 
         '2006', 
         '2007', 
         '2008', 
         '2009', 
         '2010', 
         '2011', 
         '2012']

quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
index_path = '/edgar/full-index'
ftp.cwd(index_path)

def download_file(serverpath, local_path):
    with open (local_path, 'w') as outfile:
        command = 'RETR ' + serverpath.strip()
        ftp.retrbinary(command, outfile.write)

def ensure(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def extract_and_remove(zip_path, out_dir):
    with zipfile.ZipFile(zip_path, 'r') as outzip:
        outzip.extractall(subdir)
    os.remove(zip_path)

#out_dir = sys.argv[1]
#ensure(out_dir)
#os.chdir(out_dir)

#for year in years:
#    for quarter in quarters:
#        subdir = year + '/' + quarter
#        ensure(subdir)
#        filepaths = [subdir + '/' + f for f in ('form.zip')]
#        for path in filepaths:
#            download_file(path, path)
#            extract_and_remove(path, subdir)
#

def split_list(xs, y, eq_func=lambda a, b: a == b):
    for i, x in enumerate(xs):
        if eq_func(x, y):
            return [xs[:i], xs[i + 1:]]
    else:
        return [xs]

def paths_for_10ks(index_file):
    paths = []
    lines = index_file.read().splitlines()
    lines = split_list(lines, '-+$', lambda a, b: re.match(b, a))[1]
    for line in lines:
        if line[:4] == '10-K':
            fields = re.split('\s\s+', line)
            paths.append((fields[1], fields[3], fields[4]))
    return paths

def download_10ks(data_directory):
    global ftp
    for root, dirs, files in os.walk(data_directory):
        for name in files:
            path = os.path.join(root, name)
            if path.split('.')[-1] != 'idx':
                continue
            with open(path, 'r') as index_file:
                form_paths = paths_for_10ks(index_file)
                for company, date, f in form_paths:
                    try:
                        download_file(f, os.path.join(root, '{0}_{1}'.format(company, date)))
                    except:
                        print f

#download_10ks(data)


























