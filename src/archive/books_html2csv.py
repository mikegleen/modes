# -*- coding: utf-8 -*-
"""
Convert the HTML file saved from the SH MS-Word document to a CSV file with one
column for the ObjectIdentity and one column for the new location.

Input: full path to the HTML file
Output: full path to the output XML file.
"""

import argparse
import codecs
import csv
import os.path
import re
import sys

from bs4 import BeautifulSoup as Bs

HEADING = 'Serial,Title,Author,Publisher,Date,Notes,Location'.split(',')


DEFAULT_HTML_ENCODING = 'utf-8'
VALID_LOCATIONS = ('FRAMED', 'UNKNOWN', 'QUARANTINE')
LOCATION_PATTERN = r'[A-Z]+(\d+)?\*?\??$'
SERIAL_COLUMN = 0
TITLE_COLUMN = 1
PUBLISHER_COLUMN = 3
LOCATION_COLUMN = 6
TABLE_LEN = len(HEADING)
SPECIAL_PUBLISHED = ('UNPUBLISHED', 'ROUGH SKETCH')


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def getloc(row):
    """
    Search the row from the end for the last cell that is non-empty.
    Test whether it is a valid location.
    :param row: 
    :return: valid - True or False
             cell - value of the found cell
    """
    for cell in row[::-1]:
        if not cell:
            continue
        cell = cell.upper().strip().replace(' ', '')
        if cell in VALID_LOCATIONS:
            return True, cell
        if re.match(LOCATION_PATTERN, cell):
            return True, cell
        else:
            return False, cell
    return False, ''


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
    if len(csvrow) < TABLE_LEN:
        return 2, csvrow
    if not csvrow[TITLE_COLUMN] or not csvrow[LOCATION_COLUMN]:  # if  empty
        return 3, csvrow
    if _args.prefix and not csvrow[SERIAL_COLUMN].startswith(_args.prefix):
        return 4, csvrow
    csvrow[SERIAL_COLUMN] = ''.join(csvrow[SERIAL_COLUMN].split())
    csvrow[PUBLISHER_COLUMN] = csvrow[PUBLISHER_COLUMN].strip('º')  # remove trailing garbage
    return 0, csvrow[SERIAL_COLUMN:TABLE_LEN]


def opencsvwriter(filename):
    csvfile = codecs.open(filename, 'w', 'utf-8-sig')  # insert BOM at front
    outcsv = csv.writer(csvfile, delimiter=',')
    if _args.header:
        outcsv.writerow(HEADING)
    trace(1, 'Output: {}', filename)
    return outcsv


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
        else: # elif not (len(outrow) == 1 and not outrow[0]):  # skip if just ['']
            trace(1, '----error {}: table {}, row {}, len={} {}',
                  error, tablenumber, rowcount, len(outrow), outrow)


def main():
    global tablenumber
    outcsv = opencsvwriter(_args.outfile)
    trace(1, '        input: {}', _args.infile)
    htmlfile = codecs.open(_args.infile, encoding=_args.encoding)
    soup = Bs(htmlfile, 'html.parser')  # , 'html5lib')
    tables = soup.find_all('table')
    for table in tables:
        tablenumber += 1
        one_table(table, outcsv)
    htmlfile.close()


def getargs():
    parser = argparse.ArgumentParser(description='''
        Read the HTML file saved from the MS Word "database" and create an XML
        file for inputting to Modes.
        
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
    parser.add_argument('--header', action='store_true', help='''
        Write the hard-coded header to the output CSV file before any data.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-p', '--prefix', help='''
        If specified, only rows whose Serial number starts with the prefix will
        be output.''')
    args = parser.parse_args()
    if args.prefix:
        args.prefix = args.prefix.upper()
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
