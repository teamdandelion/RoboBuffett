#!/usr/bin/env python

from ftplib import FTP
import os
import sys
import zipfile
import re
import argparse
import threading
import Queue

def connect_to_SEC(index):
    if index > 50:
        print "Maximum number of attempts exceeded. Try again later."
    else:
        try:
            return FTP('ftp.sec.gov')
        except EOFError:
            print "Connection refused on attempt {0}. Trying again...".format(index)
            return connect_to_SEC(index + 1)

<<<<<<< HEAD
=======
ftp = connect_to_SEC(0)
ftp.login()

def str_year_range(startYear, endYear):
    return map(str,range(startYear, endYear + 1))

years = str_year_range(1999, 2012) #1999 to 2012 inclusive

quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
index_path = '/edgar/full-index'
ftp.cwd(index_path)

>>>>>>> d01f96683923d7fa8a34208a88ba2c36d567a751
def download_file(serverpath, local_path):
    global ftp
    with open (local_path, 'w') as out_file:
        command = 'RETR ' + serverpath.strip()
        ftp.retrbinary(command, out_file.write)

def ensure(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def extract_and_remove(zip_path, out_dir):
    with zipfile.ZipFile(zip_path, 'r') as outzip:
        outzip.extractall(out_dir)
    os.remove(zip_path)

<<<<<<< HEAD
def download_index_files(out_dir):
    years = ['1993', '1994', '1995', '1996', 
             '1997', '1998', '1999', '2000', 
             '2001', '2002', '2003', '2004', 
             '2005', '2006', '2007', '2008', 
             '2009', '2010', '2011', '2012']
    
    quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']

    # Get the current working directory so that we can change it
    # back when we're done
    old_cwd = os.getcwd()
    ensure(out_dir)
    os.chdir(out_dir)

    for year in years:
        for quarter in quarters:
            subdir = year + '/' + quarter
            ensure(subdir)
            path = subdir + '/form.zip'
            download_file(path, path)
            extract_and_remove(path, subdir)

    os.chdir(old_cwd)

=======
out_dir = sys.argv[1]
ensure(out_dir)
os.chdir(out_dir)

for year in years:
    for quarter in quarters:
        subdir = year + '/' + quarter
        ensure(subdir)
        filepaths = [subdir + '/' + f for f in ('form.zip')]
        for path in filepaths:
            download_file(path, path)
            extract_and_remove(path, subdir)

>>>>>>> d01f96683923d7fa8a34208a88ba2c36d567a751

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
            company, date, server_path = (fields[1], fields[3], fields[4])
            paths.append((server_path, '{0}_{1}'.format(company, date)))
    return paths

def download_forms_serially(paths):
    global ftp
    for server_path, local_path in paths:
        try:
            with open(local_path, 'w') as out_file:
                ftp.retrlines('RETR ' + server_path, out_file.write)
            print "Saved: {0}".format(local_path)
        except Exception as e:
            print e
            print 'Download failed on file at: {0}'.format(server_path)

def download_10ks(data_directory):
    for root, dirs, files in os.walk(data_directory):
        for name in files:
            path = os.path.join(root, name)
            if path.split('.')[-1] != 'idx':
                continue
            with open(path, 'r') as index_file:
                form_paths = [(s, os.path.join(root, l)) for s,l in paths_for_10ks(index_file)]
                download_forms_serially(form_paths)

# A class to facilitate multithreaded downloading of data over FTP
class FTPThread(threading.Thread):
    """A class to download data over FTP in parallel threads"""
    def __init__(self, server_path, local_path):
        self.server_path = server_path
        self.local_path = local_path
        threading.Thread.__init__(self)
    def run(self):
        global ftp
        try:
            with open(self.local_path, 'w') as out_file:
                ftp.retrlines('RETR ' + self.server_path, out_file.write)
            print "Saved: {0}".format(self.local_path)
        except Exception as e:
            print e
            print 'Download failed on file at: {0}'.format(self.server_path)


def download_forms(paths, max_threads):
    finished = []
    def producer(q, paths):
        for server_path, local_path in paths:
            thread = FTPThread(server_path, local_path)
            thread.start()
            q.put(thread, True)

    def consumer(q, total_files):
        while len(finished) < total_files:
            thread = q.get(True)
            thread.join()
            finished.append(thread)

    q = Queue.Queue(max_threads)

    prod_thread = threading.Thread(target=producer, args=(q, paths))
    cons_thread = threading.Thread(target=consumer, args=(q, len(paths)))
    prod_thread.start()
    cons_thread.start()
    prod_thread.join()
    cons_thread.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download either index files (i) or form files (f) to a given directory.')
    parser.add_argument('mode', type=str, choices=['i', 'f'])
    parser.add_argument('directory', type=str)

    args = parser.parse_args()

    ftp = connect_to_SEC(0)
    ftp.login()

    if args.mode == 'i':
        index_path = '/edgar/full-index'
        ftp.cwd(index_path)
        download_index_files(args.directory)
    else:
        download_10ks(args.directory)

























