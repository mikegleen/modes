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


def one_sh_object(obj):
    """
    Update the Acquisition element of an SHxxx object that is not already
    populated.
    Set these to having come from the Simon Heneage collection.
    :param obj:
    :return: True if updated
    """
    if not object_number.startswith('SH'):
        return False
    acquisition = obj.find('./Acquisition')
    method = acquisition.find('./Method')
    if method.text:
        trace(2, 'Already populated: {}', object_number)
        return False  # don't set to default if there already is data
    person = acquisition.find('./Person')
    # sumtext = acquisition.find('./SummaryText[@elementtype="Acquisition text to be displayed"]')
    funding = acquisition.find('./Funding[@elementtype="Sponsorship"]')
    objdate = acquisition.find('./Date')
    method.text = 'purchase'
    person.text = 'Estate of Simon Heneage'
    objdate.text = '2015'
    # if sumtext is None:
    #     sumtext = ET.Element('SummaryText')
    #     acquisition.append(sumtext)
    #     sumtext.set('elementtype', 'Acquisition text to be displayed')
    # sumtext.text = ('Purchased with National Heritage Memorial Fund and'
    #                 ' ArtFund support')
    funding.text = ('Purchased with National Heritage Memorial Fund and'
                    ' ArtFund support')
    return True


def main():
    global object_number
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
        updated = False
        if object_number.startswith('SH'):
            updated = one_sh_object(oldobject)
        outfile.write(ET.tostring(oldobject, encoding='us-ascii'))
        if updated and _args.short:  # for debugging
            return
        oldobject.clear()
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
    Add Acquisition information to SHnnn records.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
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
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('Requires Python 3.6 or higher.')
    csvdict = {}  # The rows from the CSV file indexed by Serial
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()

