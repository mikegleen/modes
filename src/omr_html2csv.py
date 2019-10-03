# -*- coding: utf-8 -*-
"""
Convert an Object Movement Record (OMR) HTML file to a CSV file.
The HTML file was created by saving a DOCX file as HTML.


Input: full path to the HTML file
Output: full path to the output CSV file.
"""

import argparse
import codecs
import csv
import re

from bs4 import BeautifulSoup as Bs

DEFAULT_HTML_ENCODING = 'utf-8-sig'  # insert BOM at front

td_or_th_pat = re.compile('(td)|(th)')


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def opencsvwriter(filename):
    csvfile = codecs.open(filename, 'w', _args.encoding)
    outcsv = csv.writer(csvfile, delimiter=',')
    return outcsv


def one_table(table, outcsv):
    global tablenumber, outrowcount
    rows = table.find_all('tr')
    trace(2, 'table {}, rows: {}', tablenumber, len(rows))

    tds = rows[0].find_all('td')
    field = tds[0].p.get_text()  # Accession number JB437
    # print(f'field: "{field}"')
    objectid = re.sub(r'Accession\s+number', '', field).strip()
    # print(f'objectid: "{objectid}"')

    tds = rows[3].find_all('td')
    field = tds[0].p.get_text()
    oldloc = re.sub(r'Old\s+location', '', field).strip()

    field = tds[1].p.get_text()
    newloc = re.sub(r'New\s+location', '', field).strip()

    outrow = [objectid, oldloc, newloc]
    outcsv.writerow(outrow)
    outrowcount += 1
    trace(2, 'table {}, outrow {}', tablenumber, outrow)


def main():
    global tablenumber
    htmlfile = codecs.open(_args.infile, encoding=_args.encoding)
    trace(1, 'Input: {}', _args.infile)
    outcsv = opencsvwriter(_args.outfile)
    trace(1, 'Output: {}', _args.outfile)
    soup = Bs(htmlfile, 'html.parser')  # , 'html5lib')
    tables = soup.find_all('table')
    for table in tables:
        tablenumber += 1
        trace(3, '_args.table: {}, tablenumber: {}', _args.table, tablenumber)
        if _args.table and _args.table != tablenumber:
            continue
        one_table(table, outcsv)
    htmlfile.close()


def getargs():
    parser = argparse.ArgumentParser(description='''
        Read an HTML file and create a CSV file from the <table> elements.
        ''')
    parser.add_argument('-e', '--encoding', default=DEFAULT_HTML_ENCODING,
                        help='''
        Specify the encoding of the input HTML file and output CSV file.
        Default = "{}".
        '''.format(DEFAULT_HTML_ENCODING))
    parser.add_argument('infile', help='''
        The input HTML file''')
    parser.add_argument('outfile', help='''
        The output CSV file''')
    parser.add_argument('-t', '--table', type=int, default=0, help='''
        Select a single table to process. The default is to process all tables.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    args.prog = parser.prog
    return args


if __name__ == '__main__':
    import os
    import sys
    # print(f'cwd:{os.getcwd()}')
    assert sys.version_info >= (3, 6), 'Python must be at least 3.6'
    _args = getargs()
    rowcount = 0
    outrowcount = 0
    tablenumber = 0
    main()
    print('\nEnd {}. {} tables read, {} rows written to {}'.
          format(_args.prog.split('.')[0], tablenumber,
                 outrowcount, os.path.abspath(_args.outfile)))

