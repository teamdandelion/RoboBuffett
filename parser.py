import string

class DocError(BaseException):
    pass

def parse_quarterly_filing(filepath):
    with open(filepath, 'r') as doc:
        rawtext = doc.read()

    header_ptext = '</IMS-HEADER>' # Break the file at this text
    filer_ptext  = '\nFILER:\n' # Break filer sections at this text
    partitioned = rawtext.partition('</IMS-HEADER>')
    if partitioned[1] != '</IMS-HEADER>':
        partitioned = partitioned[0].partition('</SEC-HEADER>')
        if partitioned[1] != '</SEC-HEADER>':
            raise DocError('Unable to partition header from body')

    header_text = partitioned[0]
    document_text = partitioned[2] # This is important

    header_text = header_text.partition(filer_ptext)
    if header_text[1] != filer_ptext:
        raise DocError('Unable to partition on %s' % filer_ptext)
    filer_text  = header_text[2].partition(filer_ptext)
    header_text = header_text[0] # This is important

    filers = [] # Also important

    while filer_text[1] == filer_ptext:
        filers.append(filer_text[0])
        filer_text = filer_text[2].partition(filer_ptext)
    filers.append(filer_text[0])

    #Is there a more efficient place to define these constants?
    header_info = (
     ('DocType',         'CONFORMED SUBMISSION TYPE:' ),
     ('ReportingPeriod', 'CONFORMED PERIOD OF REPORT:'),
     ('FilingDate',      'FILED AS OF DATE:'          ))

    filer_info = (      
     ('CompanyName',     'COMPANY CONFORMED NAME:'            ),
     ('CIK',             'CENTRAL INDEX KEY:'                 ),
     ('SIC',             'STANDARD INDUSTRIAL CLASSIFICATION:'))

    header =  parse_fields(header_text, header_info)
    filers_parse = [parse_fields(x, filer_info) for x in filers]

    filers = {}
    for filer in filers_parse:
        filers[filer['CIK']] = filer

    #word_count = build_word_count(document_text)

    return (header, filers, document_text)


def build_word_count(text):
    to_remove = string.punctuation + string.digits
    text = text.translate(None, (to_remove))
    # Removes all punctuation and digits
    text = text.lower().split()
    # Splits the text into a list of lowercase words
    # Possible improvements: Strip tables, formatting (e.g. <PAGE>, - 2 -)
    num_words = len(text)
    word_count = {}
    for word in text:
        try: 
            word_count[word] += 1
        except KeyError:
            word_count[word] = 1
    # This try/except method may be somewhat more efficient than if-then branching for unigram processing. For n-grams, perhaps better to use if-then.
    return (word_count, num_words)

def parse_fields(header, property_info):
    # Defines the properties to seek in the header of the filing, and names to assign them to in the self.properties dictionary. I hope Python doesn't waste time re-creating this tuple every time parse_quarterly_filing is called.
    properties = {}
    header = header.split('\n')
    for line in header:
        line = line.strip()
        for (name, identifier) in property_info:
            if line.startswith(identifier):
                content = line.partition(identifier)[2].strip()
                # Take the content after the identifier, and strip whitespace
                properties[name] = content
    if len(properties) != len(property_info):
        missing_fields = ''
        for ptuple in property_info:
            if ptuple[0] not in properties:
                missing_fields += ',' + ptuple[0]
        raise DocError('Missing fields: %s' % missing_fields)

    return properties
