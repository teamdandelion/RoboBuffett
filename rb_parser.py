#!/usr/bin/env python
import string, re
from datetime import date
import sys # For test parsing functionality
from pdb import set_trace as debug

class ParseError(BaseException):
    pass




def parse_quarterly_filing(filepath):
    """Parse a 10-K or 10-Q. 
    Returns (header_dict, cik2filer, document_text).
    header_dict = """
    with open(filepath, 'r') as doc:
        rawtext = doc.read()
    # First partition to separate all of the header data (header + filers)
    filer_ptext  = '\nFILER:\n' # Break filer sections at this text
    partitioned = rawtext.partition('</IMS-HEADER>')
    if partitioned[1] != '</IMS-HEADER>':
        partitioned = partitioned[0].partition('</SEC-HEADER>')
        if partitioned[1] != '</SEC-HEADER>':
            raise ParseError('Unable to partition header from body')

    header_text = partitioned[0]
    document_text = partitioned[2] # Text of the document

    header_text = header_text.partition(filer_ptext)
    if header_text[1] != filer_ptext:
        raise ParseError('Unable to partition on %s' % filer_ptext)
    filer_text  = header_text[2].partition(filer_ptext)
    header_text = header_text[0] # Just the document header - filing date etc

    filers_textlist = [] # Also important

    while filer_text[1] == filer_ptext:
        filers_textlist.append(filer_text[0])
        filer_text = filer_text[2].partition(filer_ptext)
    filers_textlist.append(filer_text[0])

    #Is there a more efficient place to define these constants?
    # Defines the properties to seek in the text of the filing, and names to assign them to in the self.properties dictionary. I hope Python doesn't waste time re-creating this tuple every time parse_quarterly_filing is called.

    header_info = (
     ('DocType',         'CONFORMED SUBMISSION TYPE:' ),
     ('ReportingPeriod', 'CONFORMED PERIOD OF REPORT:'),
     ('FilingDate',      'FILED AS OF DATE:'          ))

    filer_info = (      
     ('CompanyName', 'COMPANY CONFORMED NAME:'       ),
     ('CIK',         'CENTRAL INDEX KEY:'            ),
     ('SIC',    'STANDARD INDUSTRIAL CLASSIFICATION:'))

    try:
        header_dict =  parse_fields(header_text, header_info)
        #header_dict['FilingDate'] = str2date(header_dict['FilingDate'])
    except ParseError: # Re-raise with a name
        raise ParseError('Unable to parse header')


    cik2filer = {}
    for filer in filers_textlist:
        try:
            filerdict = parse_fields(filer, filer_info)
            CIK = filerdict['CIK']
            filerdict['SIC'] = force_to_int(filerdict['SIC'])
            cik2filer[CIK] = filerdict
        except ParseError:
            pass


    if cik2filer == {}:
        raise ParseError('No valid filers')


    #word_count = build_word_count(document_text)

    return (header_dict, cik2filer, document_text)


def build_word_count(text):
    to_remove = string.punctuation + string.digits
    text = re.sub('<[^>]*>', '', text) # Remove all <Tags>
    text = text.translate(None, (to_remove))
    # Removes all punctuation and digits
    text = text.lower().split()
    # Splits the text into a list of lowercase words
    # Possible improvements: Strip tables
    num_words = len(text)
    word_count = {}
    for word in text:
        try: 
            word_count[word] += 1
        except KeyError:
            word_count[word] = 1
    # This try/except method may be somewhat more efficient than 
    # if-then branching for unigram processing. For n-grams, 
    # perhaps better to use if-then.
    return (word_count, num_words)

def parse_fields(text, property_info):
    """Parses a text, looking for specific field information
    Takes raw text, and a list of (name, identifier) tuples. 
    Returns a dictionary mapping names to the content of the line that started with 'identifier'."""
    properties = {}
    text = text.split('\n')
    for line in text:
        line = line.strip()
        for (name, identifier) in property_info:
            if line.startswith(identifier):
                content = line.partition(identifier)[2].strip()
                # Content = everything that followed the identifier
                if content == '':
                    raise ParseError('Empty field')
                properties[name] = content
                break # Move on to the next line once we find a field

    if len(properties) != len(property_info):
        raise ParseError('Unable to find all fields')
    else:
        return properties

def force_to_int(val):
    try:
        converted = int(val)
    except ValueError:
        to_remove = string.punctuation + string.letters + string.whitespace
        forced_val = val.translate(None, (to_remove))
        if forced_val == '':
            raise ParseError('Unable to convert SIC to #: %s' % val)
        converted = int(forced_val)
    return converted

def str2date(datestr):
    year  = int(datestr[0:4])
    month = int(datestr[4:6])
    day   = int(datestr[6:8])
    return date(year, month, day)

def test_parse(document):
    (header, filers, rawtext) = parse_quarterly_filing(document)
    pretty_dict(header, "header")
    [pretty_dict(x, "filer") for x in filers]
    wc = build_word_count(rawtext)
    pretty_dict(wc, "words")

def main():
    argv = sys.argv
    if len(argv) == 1:
        print "Give a document and I'll test parse it"
        exit(0)
    fpath = argv[1]
    test_parse(fpath)

def pretty_dict(output, name):
    print name + ":"
    for key, val in output.iteritems():
        print "\t" + str(key) + ": " + str(val)

if __name__ == "__main__":
    main()

