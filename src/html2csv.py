# -*- coding: utf-8 -*-
"""
Convert an HTML file to a CSV file. The first
row in the first table in the HTML file will be taken as the CSV field names.

Input: full path to the HTML file
Output: full path to the output CSV file.
"""

import argparse
import codecs
import csv
import os.path
import re
import sys

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


def handle_one_row(row):
    csvrow = []
    details = row.find_all(td_or_th_pat)
    for td in details:
        paras = td.find_all('p')
        detail = ''
        for para in paras:
            # replace whitespace with a single space
            text = ' '.join(para.text.split())
            detail += text + ' '

        if not detail:  # if there were no <p> tag(s)
            detail = td.text
        detail = detail.strip()  # remove trailing NL
        csvrow.append(detail)

    if not csvrow:
        return 1, csvrow
    if _args.inhibit_upper:
        try:
            csvrow[0] = csvrow[0].upper()
            csvrow[0] = re.sub(r'\s', '', csvrow[0])
        except IndexError:
            return 2, csvrow
    # print(csvrow)
    return 0, csvrow


def one_table(table, outcsv):
    global rowcount, tablenumber, outrowcount
    rows = table.find_all('tr')
    trace(1, 'table {}, rows: {}', tablenumber, len(rows))
    for row in rows:
        rowcount += 1
        error, outrow = handle_one_row(row)
        # ignore empty rows and title rows
        if not error:
            outrowcount += 1
            outcsv.writerow(outrow)
            trace(2, 'row {}, outrow {}', outrowcount, outrow)
        else:  # elif not (len(outrow) == 1 and not outrow[0]):  # skip if just ['']
            trace(1, '----error {}: table {}, row {}, len={} {}',
                  error, tablenumber, rowcount, len(outrow), outrow)


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
        # print(f'_args.table: {_args.table}, tablenumber: {tablenumber}')
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
    parser.add_argument('-u', '--inhibit_upper', action='store_false',
                        default=True, help='''
        By default, the first column is converted to upper case and white
        space characters are removed.
        If specified, inhibit this conversion.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    _args = getargs()
    rowcount = 0
    outrowcount = 0
    tablenumber = 0
    assert sys.version_info >= (3, 6)
    main()
    print('\nEnd html2csv. {} rows read, {} rows written to {}'.
          format(rowcount, outrowcount, os.path.abspath(_args.outfile)))


