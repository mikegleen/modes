# -*- coding: utf-8 -*-
"""
Convert the HTML file saved from an MS-Word document to a CSV file. The first
row in the first table in the HTML file will be taken as the CSV field names.

Input: full path to the HTML file
Output: full path to the output XML file.
"""

import argparse
import codecs
import csv
import os.path
import sys

from bs4 import BeautifulSoup as Bs

DEFAULT_HTML_ENCODING = 'utf-8'


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def handle_one_row(row):
    csvrow = []
    details = row.find_all('td')
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
    # print(csvrow)
    return 0, csvrow


def opencsvwriter(filename):
    csvfile = codecs.open(filename, 'w', 'utf-8-sig')  # insert BOM at front
    outcsv = csv.writer(csvfile, delimiter=',')
    trace(1, 'Output: {}', filename)
    return outcsv


def one_table(table, outcsv):
    global rowcount, tablecount, outrowcount
    rows = table.find_all('tr')
    trace(1, 'table {}, rows: {}', tablecount, len(rows))
    for row in rows:
        rowcount += 1
        error, outrow = handle_one_row(row)
        # ignore empty rows and title rows
        if not error:
            outrowcount += 1
            outcsv.writerow(outrow)
        else:  # elif not (len(outrow) == 1 and not outrow[0]):  # skip if just ['']
            trace(1, '----error {}: table {}, row {}, len={} {}',
                  error, tablecount, rowcount, len(outrow), outrow)


def main():
    global tablecount
    outcsv = opencsvwriter(_args.outfile)
    trace(1, '        input: {}', _args.infile)
    htmlfile = codecs.open(_args.infile, encoding=_args.encoding)
    soup = Bs(htmlfile, 'html.parser')  # , 'html5lib')
    tables = soup.find_all('table')
    for table in tables:
        tablecount += 1
        one_table(table, outcsv)
    htmlfile.close()


def getargs():
    parser = argparse.ArgumentParser(description='''
        Read the HTML file saved from the MS Word "database" and create a CSV
        file for converting to XML for inputting to Modes.

        When saving the HTML file from MS Word, make sure to set the output
        character encoding to utf-8. Otherwise, specify the -e parameter.
        ''')
    parser.add_argument('-e', '--encoding', default=DEFAULT_HTML_ENCODING,
                        help='''
        Specify the encoding of the input HTML file.
        Default = "{}".
        '''.format(DEFAULT_HTML_ENCODING))
    parser.add_argument('infile', help='''
        The HTML file saved from MS Word''')
    parser.add_argument('outfile', help='''
        The output CSV file''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    _args = getargs()
    rowcount = 0
    outrowcount = 0
    tablecount = 0
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    main()
    print('\nEnd html2csv. {} rows read, {} rows written to {}'.
          format(rowcount, outrowcount, os.path.abspath(_args.outfile)))


