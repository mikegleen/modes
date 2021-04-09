"""
    Create a list of accession numbers of objects displayed at the Dulwich
    Museum by fuzzy matching the title from the catalog with the titles in
    the Modes database.
"""
import codecs
import csv
from fuzzywuzzy import process
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfgutil import Stmt

INTXTFILENAME = 'data/geoff/dulwich_1.txt'
INXMLFILENAME = 'results/xml/pretty/2021-02-24_water_pretty.xml'
OUTCSVFILENAME = 'results/csv/exhibitions/dulwich.csv'
TRACE = 1
MINSCORE = 90
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


def main():
    outcsv = codecs.open(OUTCSVFILENAME, 'w', encoding='utf-8-sig')
    outcsvwriter = csv.writer(outcsv)

    intxtfile = open(INTXTFILENAME)
    iddict = readxml()
    titles = iddict.keys()
    nfound = nofind = 0
    outcsvwriter.writerow(['Suggested', 'Manual',
                           'Catalog #', 'Score', 'Title in Catalog'])
    for line in intxtfile:
        if (m := re.match(r'(\d+)\.\s*(.*)', line)) is None:
            print(f'\n\n**********{line}')
            outcsvwriter.writerow(['', '', '', line])
            continue
        if 'Private' in line:
            continue
        catalognum = m.group(1)
        title = m.group(2)
        # title = re.sub(r'[^\w\s]', '', m.group(2))
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
            print(f'\n{line.strip()}')
            print(f'{found_id if found else "nofind"}:'
                  f'{edited}')
            outrow = [found_id, '', catalognum, bestscore, line[:80]]
            outcsvwriter.writerow(outrow)
    print(f'{nfound=}, {nofind=}')
    print(f'{nfound=}, {nofind=}', file=sys.__stderr__)
    print(f'CSV written to {OUTCSVFILENAME}', file=sys.__stderr__)


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    main()
