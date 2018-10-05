# -*- coding: utf-8 -*-
"""
CSV file columns: Serial,Title,Medium,Date Acquired,From,Price

"""
import argparse
import codecs
import csv
from datetime import datetime
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def normalize_date(indate):
    indate = ' '.join(indate.split())  # clean whitespace
    datestr = ''
    try:
        trydate = datetime.strptime('%d %b %Y', indate)  # 1 Jun 2001
        day = str(trydate.day)
        month = str(trydate.month)
        year = str(trydate.year)
        datestr = f'{day}.{month}.{year}'  # no leading zeros
    except ValueError:
        pass
    if not datestr:
        try:
            trydate = datetime.strptime('%b %Y', indate)  # Jun 2001
            month = str(trydate.month)
            year = str(trydate.year)
            datestr = f'{month}.{year}'
        except ValueError:
            pass
    return datestr


def one_csv_row(row):
    if not row['Serial'].startswith('JB'):
        return
    datestr = normalize_date(row['Date Acquired'])
    price = re.sub('£', '', row['Price'])
    price = re.sub(',', '', price)
    row['Date Acquired'] = datestr
    row['Price'] = price
    csvdict[row['Serial'].strip()] = row


def one_object(obj, serial):
    acquisition = obj.find('./Acquisition')
    row = csvdict[serial]
    if row['Date Acquired']:
        da = acquisition.find('./Date')
        da.text = row['Date Acquired']
    person = acquisition.find('./Person')
    person.text = row['From'].strip()
    method = acquisition.find('./Method')
    price = row['Price']
    if price.isnumeric():
        method.text = 'purchase'
        priceelt = ET.Element('Price')
        priceelt.text = price
        acquisition.insert(4, priceelt)
    else:
        method.text = price


def main():
    # with open(_args.csvfile, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        one_csv_row(row)
    outfile.write(b'<?xml version="1.0" encoding="utf-8"?>\n<Interchange>\n')
    for event, oldobject in ET.iterparse(infile):
        if oldobject.tag != 'Object':
            continue
        numelt = oldobject.find('./ObjectIdentity/Number')
        if numelt is not None:
            object_number = numelt.text
        else:
            object_number = 'Missing'
            trace(1, 'Missing "{}"', object_number)
        trace(2, '**** {}', object_number)
        if numelt == 'JB607':
            pass
        if object_number in csvdict:
            one_object(oldobject, object_number)
            outfile.write(ET.tostring(oldobject, encoding='us-ascii'))
            if _args.short:  # for debugging
                return
        oldobject.clear()
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''

        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-c', '--csvfile', required=True,
                        help='''
        The CSV file containing the acquisitions register to be applied.''')
    parser.add_argument('-f', '--force', action='store_true', help='''
        Replace existing values. If not specified only empty elements will be
        inserted. ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    csvdict = {}  # The rows from the CSV file indexed by Serial
    _args = getargs()
    csvfile = codecs.open(_args.csvfile, 'r', 'utf-8-sig')
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()

