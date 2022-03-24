"""
    Create a list of accession numbers of objects in the PE changeover
    by fuzzy matching the title from the catalog with the titles in
    the Modes database using the Levenshtein Distance algorithm.
"""
import codecs
import csv
from fuzzywuzzy import process
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfgutil import Stmt

INCSVFILENAME = 'results/csv/changeover_pe.csv'
INXMLFILENAME = 'prod_update/normal/2022-03-15_batch002.xml'
OUTCSVFILENAME = 'results/csv/changeover_pe_x.csv'
TRACE = 1
MINSCORE = 80
PRINTFOUND = True
PRINTNOTFOUND = True


def trace(level, template, *args):
    if TRACE >= level:
        print(template.format(*args))


def readxml():
    inxmlfile = open(INXMLFILENAME)
    iddict = {}
    for event, elem in ET.iterparse(inxmlfile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find(Stmt.get_default_record_id_xpath())
        idnum = idelem.text if idelem is not None else None
        trace(3, 'idnum: {}', idnum)
        title = elem.find('./Identification/Title')
        if title is not None and title.text is not None:
            text = title.text
            # print(text, type(text), file=sys.__stderr__)
            # text = re.sub(r'[^\w\s]', '', title.text)
            iddict[text] = idnum
        else:
            print(f'Title or title.text are None: {idnum}')
    return iddict


def one_obj(s: str):
    pass


def main():

    incsvfile = codecs.open(INCSVFILENAME, 'r', 'utf-8-sig')
    inreader = csv.reader(incsvfile)
    current, replacement = 'Current Image,Replacement Image'.split(',')
    iddict = readxml()
    titles = iddict.keys()
    nfound = nofind = 0
    outcsvwriter.writerow(['Current Suggested', 'Current Manual',
                           'Current Catalog #', 'Current Score', 'Current Title in Catalog',
                           'Replacement Suggested', 'Replacement Manual',
                           'Replacement Catalog #', 'Replacement Score', 'Replacement Title in Catalog',
                           ])
    next(inreader)  # skip header
    outrow = None
    for row in inreader:
        print(row)
        if not row[0]:
            continue
        if 'remain' in row[1].lower():
            print(f'Skipping {row}')
            continue
        for n in (0, 1):
            title = ' '.join(row[n].split())
            if (m := re.match(r'(\d+)\.\s*(.*)', title)) is None:
                print(f'\n\nnomatch 1 n={n} **********{row}')
                continue
            catalognum = m.group(1)
            title = m.group(2)
            # title = re.sub(r'[^\w\s]', '', m.group(2))
            if (m := re.match(r'(.*?)\d+\s?x\s?\d+.*', title)) is None:
                print(f'\n\nnomatch 2 n={n} **********{row}')
                continue
            title = m.group(1)  # strip trailing 16 x 22ins...
            extracted = process.extract(title, titles, limit=2)
            best, bestscore = extracted[0]
            nextbest, nextscore = extracted[1]
            edited = []
            for ttl, score in extracted:
                edited.append((iddict[ttl], ttl[:50], score))
            if best in iddict and bestscore >= MINSCORE:
                found = True
                found_id = iddict[best]
                if nextscore >= MINSCORE:
                    print(f'Warning: {found_id} next score >= {MINSCORE} '
                          f'next best: {iddict[nextbest]}')
                nfound += 1
            else:
                found = False
                found_id = ''
                nofind += 1
            if (found and PRINTFOUND) or (not found and PRINTNOTFOUND):
                print(f'\n{row[n].strip()}')
                print(f'{found_id if found else "nofind"}:'
                      f'{edited}')
                if n == 0:
                    outrow = [found_id, '', catalognum, bestscore, title[:80]]
                else:
                    outrow += [found_id, '', catalognum, bestscore, title[:80]]
                    outcsvwriter.writerow(outrow)
    print(f'{nfound=}, {nofind=}')
    print(f'{nfound=}, {nofind=}', file=sys.__stderr__)
    print(f'CSV written to {OUTCSVFILENAME}', file=sys.__stderr__)


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    outcsv = codecs.open(OUTCSVFILENAME, 'w', encoding='utf-8-sig')
    outcsvwriter = csv.writer(outcsv)
    main()
