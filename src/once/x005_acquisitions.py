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


def normalize_csv_date(indate):
    indate = ' '.join(indate.split())  # clean whitespace
    if not indate:
        return ''
    datestr = ''
    try:
        trydate = datetime.strptime(indate, '%d %b %Y')  # 1 Jun 2001
        day = str(trydate.day)
        month = str(trydate.month)
        year = str(trydate.year)
        datestr = f'{day}.{month}.{year}'  # no leading zeros
    except ValueError:
        pass
    if not datestr:
        try:
            trydate = datetime.strptime(indate, '%b %Y')  # Jun 2001
            month = str(trydate.month)
            year = str(trydate.year)
            datestr = f'{month}.{year}'
        except ValueError:
            print(f'object: {object_number}, failed scan: {indate}')
    return datestr


def one_csv_row(row):
    if not row['Serial'].startswith('JB'):
        return
    datestr = normalize_csv_date(row['Date Acquired'])
    price = re.sub('£', '', row['Price'])
    price = re.sub(',', '', price)
    row['Date Acquired'] = datestr
    row['Price'] = price
    csvdict[row['Serial'].strip()] = row


def one_object_from_csv(obj, serial):
    """
    Update an Object element with the data from a row in the CSV file.
    :param obj: The Object instance.
    :param serial: This object's serial number which is an index into csvdict.
    :return: True. The Object instance is updated.
    """
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
    return True  # the object is updated


def one_other_object(obj):
    """
    Update the Acquisition element of a JBxxx object not in the CSV file.
    Set these to having come from the Joan Brinsmead collection.
    :param obj:
    :return: True if updated
    """
    if not object_number.startswith('JB'):
        return False
    acquisition = obj.find('./Acquisition')
    method = acquisition.find('./Method')
    if method.text:
        return False  # don't set to default if there already is data
    person = acquisition.find('./Person')
    sumtext = acquisition.find('./SummaryText[@elementtype="Acquisition text to be displayed"]')
    objdate = acquisition.find('./Date')
    method.text = 'gift'
    person.text = 'Denis Brinsmead'
    objdate.text = '1992'
    if sumtext is None:
        sumtext = ET.Element('SummaryText')
        acquisition.append(sumtext)
        sumtext.set('elementtype', 'Acquisition text to be displayed')
    sumtext.text = 'Part of the Joan Brinsmead collection'
    return True


def main():
    global object_number
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
        if object_number in csvdict:
            trace(2, 'incsv: {}', object_number)
            one_object_from_csv(oldobject, object_number)
        else:
            trace(2, 'not incsv: {}', object_number)
            one_other_object(oldobject)
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

