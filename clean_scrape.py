from ftplib import FTP
from tempfile import NamedTemporaryFile
from itertools import *
import sys
import os
import zipfile
import subprocess

hosts = ['altair.cs.uchicago.edu', 'ursa.cs.uchicago.edu',
         'ankaa.cs.uchicago.edu', 'antares.cs.uchicago.edu',
         'arcturus.cs.uchicago.edu', 'as.cs.uchicago.edu',
         'avior.cs.uchicago.edu', 'be.cs.uchicago.edu',
         'betelgeuse.cs.uchicago.edu', 'canopus.cs.uchicago.edu',
         'capella.cs.uchicago.edu', 'da.cs.uchicago.edu',
         'deneb.cs.uchicago.edu', 'dubhe.cs.uchicago.edu',
         'gacrux.cs.uchicago.edu', 'hadar.cs.uchicago.edu',
         'ki.cs.uchicago.edu', 'mimosa.cs.uchicago.edu',
         'naos.cs.uchicago.edu', 'polaris.cs.uchicago.edu',
         'procyon.cs.uchicago.edu', 'rastaban.cs.uchicago.edu',
         're.cs.uchicago.edu', 'rigel.cs.uchicago.edu',
         'saiph.cs.uchicago.edu', 'sh.cs.uchicago.edu',
         'sirius.cs.uchicago.edu', 'ul.cs.uchicago.edu']

def connect_to_SEC(max_attempts=50):
    """ Connect to the SEC ftp server, timing out after max_attempts
    attempts."""
    for i in xrange(max_attempts):
        try:
            return FTP('ftp.sec.gov')
        except EOFError:
            pass
    print "Maximum number of attempts exceeded. Try again later."


def download_file(server_path, local_path):
    """Download a file at server_path on the global ftp server object
    to local_path."""
    global ftp
    with NamedTemporaryFile(delete=False) as out_file:
        temp_file_name = out_file.name
        ftp.retrbinary('RETR ' + server_path, out_file.write)
    os.rename(temp_file_name, local_path)
    print "Succesfully downloaded to {0}".format(local_path)


def ensure(dir):
    """Create a directory if it does not exist"""
    if not os.path.exists(dir):
        os.makedirs(dir)


def extract_and_remove(zip_path, out_dir):
    """Extract the zip file at zip_path to out_dir and then delete it"""
    with zipfile.ZipFile(zip_path, 'r') as outzip:
        outzip.extractall(out_dir)
    os.remove(zip_path)


def download_index_files(out_dir):
    """Download all of the SEC index files, organizing them into a
    directory structure rooted at out_dir."""

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


dropuntil = lambda pred, xs: dropwhile(lambda x: not pred(x), xs)


def paths_for_10ks(index_file):
    paths = []
    # drop the header of the index file, which is seperated from the
    # body by a line of all '-'s
    lines = dropuntil(lambda a: re.match('-+$', a), index_file)
    lines.next()
    for line in lines:
        if line[:4] == '10-K' or line[:4] == '10-Q':
            fields = re.split('\s\s+', line)
            company, date, server_path = (fields[1], fields[3], fields[4])
            paths.append((server_path, '{0}_{1}_{2}'.format(company.replace('/', '-'), date, fields[0].replace('/','-'))))
    return paths


# Actually don't think I need this
def ssh_setup(user, password):
    global hosts
    command = 'ssh-keygen -t rsa; cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys'
    for host in hosts:
        subprocess.call(['ssh', '{0}@{1}'.format(user, host), command])
    




















