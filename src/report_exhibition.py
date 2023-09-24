"""


"""
import codecs
from collections import namedtuple, defaultdict
import csv
import sys
from colorama import Fore, Style
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfgutil import Stmt
from utl.normalize import normalize_id, denormalize_id


def trace(level, template, *args, color=None):
    if verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def main():
    tally = defaultdict(list)
    titles = {}
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find(Stmt.get_default_record_id_xpath())
        idnum = idelem.text  # if idelem is not None else None
        idnum = normalize_id(idnum)
        titleelem = elem.find('./Identification/Title')
        title = ''
        if titleelem is not None:
            title = titleelem.text
        titles[idnum] = title
        trace(3, 'idnum: {}', idnum)
        exhibs = elem.findall('./Exhibition')
        for exhib in exhibs:
            exhibname = exhib.find('./ExhibitionName')
            if exhibname is None:
                continue
            text = exhibname.text
            exhibplace = exhib.find('./Place')
            if exhibplace is not None:
                place = exhibplace.text
                if place and place != 'HRM':
                    text = f'{text} ({place})'
            tally[idnum].append(text)
    stally = sorted(list(tally.items()), key=lambda x: len(x[1]), reverse=True)
    outwriter.writerow(['Serial', 'Title'])
    for row in stally:
        outrow = [denormalize_id(row[0]), titles[row[0]]] + row[1]
        outwriter.writerow(outrow)


if __name__ == '__main__':
    assert sys.version_info >= (3, 11)
    verbose = 1
    infile = open(sys.argv[1])
    outfile = codecs.open(sys.argv[2], 'w', 'utf-8-sig')
    outwriter = csv.writer(outfile)
    trace(1, 'Input file: {}', infile.name)
    main()
    trace(1, 'End report_exhibition.py.', color=Fore.GREEN)
