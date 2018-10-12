# -*- coding: utf-8 -*-
"""
    Convert all dd-mm-yyyy format dates to Modes format d.m.yyyy.
"""

import argparse
from datetime import datetime as dt
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars
# from utl import normalize_date as nd
import utl.normalize_date as nd


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_object(obj):
    db = obj.find(
        './ObjectLocation[@elementtype="current location"]/Date/DateBegin')
    if db is not None and db.text is not None:
        isodate = None
        try:
            isodate = dt.strptime(db.text, '%Y-%m-%d')
        except ValueError:
            pass
        if isodate:
            db.text = nd.modesdate(isodate)


def main():
    global object_number
    outfile.write(b'<?xml version="1.0"?>\n<Interchange>\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        numelt = elem.find('./ObjectIdentity/Number')
        if numelt is not None:
            object_number = numelt.text
        else:
            object_number = 'Missing'
            trace(1, 'Missing "{}"', object_number)
        one_object(elem)
        outfile.write(ET.tostring(elem, encoding='us-ascii'))
        if _args.newline:
            outfile.write(b'\n')
        if _args.short:
            break
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Modify the XML structure.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-n', '--newline', action='store_true', help='''
        If set, add a newline character at the end of each object element.
        ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
