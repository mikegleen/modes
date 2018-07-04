# -*- coding: utf-8 -*-
"""
Convert the HTML file saved from the JB MS-Word document to a CSV file with one
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

DEFAULT_HTML_ENCODING = 'utf-8'
VALID_LOCATIONS = ('FRAMED', 'UNKNOWN', 'LOANED')
LOCATION_PATTERN = r'[A-Z]+\d+\*?\??$'


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))

# print(len(rows), rows[2])


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
        cell = cell.strip().upper()
        ucell = ' '.join(cell.split())
        if ucell in VALID_LOCATIONS:
            return True, cell
        if re.match(LOCATION_PATTERN, ucell):
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
            ptext = para.text
            text = ' '.join(ptext.split())
            detail += text + '\n'
        if not detail:  # if there was no <p> tag
            detail = td.text
        detail = detail.strip()  # remove trailing NL
        csvrow.append(detail)

    if not csvrow:
        return False, csvrow
    # print(csvrow)
    try:
        locrow = [csvrow[0].upper().replace(' ', '')]
    except IndexError:
        return False, csvrow
    if _args.prefix and not locrow[0].startswith(_args.prefix):
        return False, locrow
        # print('***', goodrow, locrow)
    goodrow, location = getloc(csvrow)
    if goodrow:
        locrow.append(location)
        try:
            locrow.append(csvrow[2])  # Medium
        except IndexError:
            print(csvrow)
            sys.exit()
    return goodrow, locrow


def opencsvwriter(filename):
    # csvfile = open(filename, 'w', newline='')
    csvfile = codecs.open(filename, 'w', 'utf-8-sig')  # insert BOM at front
    outcsv = csv.writer(csvfile, delimiter=',')
    # outcsv.writerow(HEADING)
    trace(1, 'Output: {}', filename)
    return outcsv


def one_table(table, outcsv):
    global rowcount, tablecount, outrowcount
    rows = table.find_all('tr')
    trace(1, 'table {}, rows: {}', tablecount, len(rows))
    for row in rows:
        trace(3,'----trace: {}', row)
        rowcount += 1
        goodrow, outrow = handle_one_row(row)
        # ignore empty rows and title rows
        if goodrow:
            trace(2,'---- goodrow: {}', outrow)
            outrowcount += 1
            outcsv.writerow(outrow)
        else: # elif not (len(outrow) == 1 and not outrow[0]):  # skip if just ['']
            trace(1, '----skipping table {}, row {}, len={} {}',
                  tablecount, rowcount, len(outrow), outrow)


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


def getargs(argv):
    parser = argparse.ArgumentParser(description='''
        Read the HTML file saved from the MS Word "database" and create an XML
        file for inputting to Modes.
        ''')
    parser.add_argument('infile', help='''
        The HTML file saved from MS Word''')
    parser.add_argument('outfile', help='''
        The output CSV file''')
    parser.add_argument('-e', '--encoding', default=DEFAULT_HTML_ENCODING,
                        help='''
        Specify the encoding of the input HTML file.
        Default = "{}".
        '''.format(DEFAULT_HTML_ENCODING))
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
    _args = getargs(sys.argv)
    rowcount = 0
    outrowcount = 0
    tablecount = 0
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    main()
    print('\nEnd html2csv. {} rows read, {} rows written to {}'.
          format(rowcount, outrowcount, os.path.abspath(_args.outfile)))


