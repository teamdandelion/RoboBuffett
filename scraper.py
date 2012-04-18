from ftplib import FTP
import os
import sys
import zipfile

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

def downloadfile(serverpath, local_path):
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

out_dir = sys.argv[1]
ensure(out_dir)
os.chdir(out_dir)

for year in years:
    for quarter in quarters:
        subdir = year + '/' + quarter
        ensure(subdir)
        filepaths = [subdir + '/' + f for f in ('form.zip')]
        for path in filepaths:
            downloadfile(path, path)
            extract_and_remove(path, subdir)


def download_10ks(data_directory):
    global ftp
    for root, dirs, files in os.walk(data_directory):




























