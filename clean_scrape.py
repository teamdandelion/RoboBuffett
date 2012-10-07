from ftplib import FTP
from tempfile import NamedTemporaryFile
from itertools import *
import sys
import os
import zipfile
import subprocess
from contextlib import contextmanager


@contextmanager
def directory(path):
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)

# run with -c for client mode

# Initialize a variable called ftp so that we can access it from
# any function after setting it to an FTP object in main
ftp = None

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
    attempts.
    """
    for i in xrange(max_attempts):
        try:
            return FTP('ftp.sec.gov')
        except EOFError:
            pass
    print "Maximum number of attempts exceeded. Try again later."


def download_file(server_path, local_path):
    """Download a file at server_path on the global ftp server object
    to local_path.
    """
    global ftp
    with NamedTemporaryFile(delete=False) as out_file:
        temp_file_name = out_file.name
        ftp.retrbinary('RETR ' + server_path, out_file.write)
    os.rename(temp_file_name, local_path)
    print "Succesfully downloaded to {0}".format(local_path)


def ensure(dir):
    """Create a directory if it does not exist
    """
    if not os.path.exists(dir):
        os.makedirs(dir)


def extract_and_remove(zip_path, out_dir):
    """Extract the zip file at zip_path to out_dir and then delete it
    """
    with zipfile.ZipFile(zip_path, 'r') as outzip:
        outzip.extractall(out_dir)
    os.remove(zip_path)


def download_index_files(out_dir):
    """Download all of the SEC index files, organizing them into a
    directory structure rooted at out_dir.
    """

    years = ['1993', '1994', '1995', '1996', 
             '1997', '1998', '1999', '2000', 
             '2001', '2002', '2003', '2004', 
             '2005', '2006', '2007', '2008', 
             '2009', '2010', '2011', '2012']

    quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']

    ensure(out_dir)

    with directory(out_dir):
        for year in years:
            for quarter in quarters:
                subdir = year + '/' + quarter
                ensure(subdir)
                path = subdir + '/form.zip'
                download_file(path, path)
                extract_and_remove(path, subdir)



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


def create_paths_file(data_dir, out_path):
    """Walk the data directory to create file with one 2-tuple per line 
    that contains the server path and intended local path of each form
    in the index file.
    """
    seperator = '!!!'
    with open(out_path, 'a') as out_file:
        for root, dirs, files in os.walk(data_dir):
            for name in files:
                path = os.path.join(root, name)
                if path.split('.')[-1] != 'idx':
                    continue
                with open(path, 'r') as index_file:
                    form_paths = [(s, os.path.join(root, l)) for s,l in paths_for_10ks(index_file)]
                    outfile.write('\n'.join(str(t) for t in form_paths) + '\n')


def chunkify_paths_file(paths_file_path, num_chunks, out_dir):
    """Split the paths files at paths_file_path into the specified number
    of chunks, placing the chunks in out_dir
    """  
    with open(paths_file_path, 'r') as paths_file:
        num_lines = sum(1 for line in paths_file)
        paths_file.seek(0)
        chunk_size = num_lines / num_chunks
        for i in xrange(num_chunks):
            with open(os.path.join(out_dir, 'paths{0}.txt'.format(i)), 'w') as p:
                p.write(''.join(islice(paths_file, 0, chunk_size)))
        with open(os.path.join(out_dir, 'paths{0}'.format(num_chunks)), 'w') as p:
                p.write(''.join(paths_file))    


def client_procedure(chunk_number, chunks_dir):
    with open('paths{0}.txt'.format(chunk_number), 'r') as chunk:
        for line in chunk:
            try:
                s, l = eval(line)
            except Exception as e:
                sys.stderr.write(str(e) + line)
            else:
                try:
                    download_file(s, l)
                except Exception as e: # Maybe add specific exceptions here but I think catching all is better
                    sys.stderr.write(str(e) + line)


# rename this function
# have a variable for the pollux loop like script
def start_download_on_hosts(consolidator, main_data_dir, hosts, chunks_dir, temp_data_dir, script_path, log_dir):
    chunk_paths = [os.path.join(chunks_dir, c) for c in os.listdir(chunks_dir)]
    # see if there isn't a less hackish way of doing this
    command = ('ssh {h} ' + '"nohup python {0}'.format(script_path)
              + ' -c {n}"' + ' >' + log_dir + '/log{n}' + ' 2>' + log_dir + '/err{n}&')

    # This is possibly a bad idea
    consolidator_loop = ('"while true; do '
                             'rsync -av --remove-source-files {temp}; '
                             'sleep 2; '
                         'done"')

    subprocess.call('ssh {0} '.format(consolidator) + consolidator_loop)

    for i, (host, chunk_path) in enumerate(zip(hosts, chunk_paths)):
        subprocess.call(command.format(h=host, n=i))

def main():
    global ftp
    usage = ('Download either index files (i) or form files (f) '
             'to a given directory, or run in client mode (c).')
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('mode', type=str, choices=['i', 'f', 'c'])
    parser.add_argument('directory', type=str)

    args = parser.parse_args()

    ftp = connect_to_SEC(0)
    ftp.login()

