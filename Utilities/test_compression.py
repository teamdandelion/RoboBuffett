#!/usr/bin/env python
'''Test compression strategies, counter vs dict, etc'''
import os, sys, logging, string, time, copy, gc
from datetime import date, timedelta
from pdb import set_trace as debug
from collections import Counter
# Note: Using Counter on the test dataset increased the pickled size from 1.3mb to 1.8mb
try:
    import cPickle as pickle
except:
    import pickle

# Change this below robobuffet_directory = '/Users/danmane/Documents/Code/Git/RoboBuffett'

def printandlog(msg):
    logging.info(msg)
    print msg

def floatRange(minv, maxv, step):
    """Not reliable for heavy-duty use due to floating point oddities"""
    x = minv
    while x <= maxv+step:
        yield x
        x += step


class DictDoc:
    def __init__(self):
        self.word_count = {}
        self.num_words = 0

    def makeCopy(self, original):
        self.num_words = original.num_words
        self.word_count = original.word_count.copy()

    def generate(self, path):
        with open(path, 'r') as f:
            text = f.read()
        to_remove = string.punctuation + string.digits
        text = text.translate(None, (to_remove))
        # Removes all punctuation and digits
        text = text.lower()
        text = text.split()
        # Splits the text into a list of lowercase words
        # Possible improvements: Strip tables, formatting (e.g. <PAGE>, - 2 -)
        self.num_words = len(text)
        for word in text:
            try: 
                self.word_count[word] += 1
            except KeyError:
                self.word_count[word] = 1

    def delete(self):
        del self.word_count
        del self.num_words

class ContDoc:
    def __init__(self, path):
        with open(path, 'r') as f:
            text = f.read()
        to_remove = string.punctuation + string.digits
        text = text.translate(None, (to_remove))
        # Removes all punctuation and digits
        text = text.lower()
        text = text.split()
        self.num_words = len(text)
        self.word_count = Counter(text)

def main(data_dir):
    rb_dir = '/Users/danmane/Documents/Code/Git/RoboBuffett'
    os.chdir(rb_dir)
    #with open('./Utilities/compression.log', 'w') as cleanlog:
    #    pass # Empty the log before each run

    logging.basicConfig(filename='./Utilities/compression.log', level=logging.INFO)
    files = os.listdir(data_dir)

    #docs = process_file_set(files, 'Utilities/dict.dat', DictDoc, 'Naive Dictionary:', data_dir)    
    #process_file_set(files, 'Utilities/cont.dat', DictDoc, 'Naive Container:', data_dir)   
    #print "About to load from pickle"
    
    print "About to start range"
    
    # s1 = time.time()
    # cheapcopy = dictlist_copy(docs)
    # s2 = time.time()
    # print "cheap:  %f" % (s2-s1)
    # docscopy = copy.deepcopy(docs)
    # s3 = time.time()
    #print "regular: %f" % (s3-s2)
    
    for t in floatRange(.05, .95, .1):
        docs = load_docs_from_file()
        print "Finished load for threshold %f" %t
        test_compression(docs, t)
        for doc in docs:
            doc.delete()
        del docs

def load_docs_from_file():
    with open('Utilities/dict.dat', 'r') as f:
        docs = pickle.load(f)
    return docs

def dictlist_copy(docs):
    outdocs = []
    for doc in docs:
        new_doc = DictDoc()
        new_doc.makeCopy(doc)
        outdocs.append(new_doc)
    return outdocs


def test_compression(docs, threshold):
    print "Starting compression for threshold %f" % threshold
    start = time.time()
    index_list_and_dict = generate_word_index(docs, threshold)
    with open('./Utilities/index.dat', 'w') as f:
        pickle.dump(index_list_and_dict, f, 2)

    index_dict = index_list_and_dict[1]
    
    compress_dict_set(docs, index_dict)
    with open('./Utilities/compressed_dict.dat', 'w') as f:
        pickle.dump(docs, f, 2)
    end = time.time()
    printandlog('Compressedion with threshold %f:' % threshold)
    printandlog('Time elapsed: %f' % (end-start))

    size = os.stat('./Utilities/compressed_dict.dat').st_size
    size += os.stat('./Utilities/index.dat').st_size
    size /= float(10**6)
    printandlog('Size: %f' % size)

def process_file_set(files, dbFile, Dtype, type_descr, data_dir):
    print "Processing %s" % type_descr
    start = time.time()
    docs = []
    n_total = len(files)
    count = 0
    for fpath in files:
        if fpath[0] != '.':
            new_obj = Dtype()
            new_obj.generate((data_dir + '/' + fpath))
            docs.append(new_obj)
        count += 1
        if count % 100 == 0:
            print "%d of %d" % (count, n_total)

    with open(dbFile, 'w') as f:
        pickle.dump(docs, f, 2)
    end = time.time()
    size = os.stat(dbFile).st_size
    size /= float(10**6)
    elapsed = end-start
    printandlog(type_descr)
    printandlog('Time elasped: %f' % elapsed)
    printandlog('Pickled size: %f' % size)
    return docs

def compress_dict_set(docs, idx_dict):
    for doc in docs:
        doc.word_list = [0] * len(idx_dict)
        for word, count in doc.word_count.copy().iteritems():
            try:
                idx = idx_dict[word]
                doc.word_list[idx] = count
                del doc.word_count[word]
            except KeyError:
                pass

def generate_word_index(dict_set, threshold):
    """Generates an index of commonly used words in the documents, so that the documents can be stored in compressed form. We can remove all instances of commonly used words from the dictionaries, and add a k-tuple of word counts, where k is the number of commonly used words. THRESHOLD determines what proportion of documents a word must be in for it to be included in the list.
    Creates self.index_list, an ordered list of words in the index. Creates self.index_dict which maps from element indicies back to the right word in the sequence. Sets self.indexed = 1."""
    # Threshold in (0, 1)
    start = time.time()
    dict_index = {}
    threshold *= len(dict_set)
    for document in dict_set:
        for word in document.word_count.iterkeys():
            try: 
                dict_index[word] += 1
            except KeyError:
                dict_index[word]  = 1
    index_list = []
    for word, val in dict_index.iteritems():
        if val > threshold:
            index_list.append(word)
    del dict_index
    index_list.sort()
    index_dict = {}
    for i in xrange(len(index_list)):
        index_dict[index_list[i]] = i
    end = time.time()
    #printandlog('Dict Index time elapsed: %f' % (end-start))
    return (index_list, index_dict)

if __name__ == "__main__":
    main('BigData')


