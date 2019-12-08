# -*- coding: utf-8 -*-
"""
    If an ObjectLocation has a DateEnd element, set the ObjectLocation elementtype
    to "previous location".
"""

import argparse
from datetime import datetime as dt
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars
# from utl import normalize_date as nd
import utl.normalize as nd


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def writeout(bstr):
    if outfile:
        outfile.write(bstr)


def one_object(obj):
    """
    If a current location has a DateEnd element, change it to "previous location".
    :param obj:
    :return:
    """
    updated = False
    objectlocations = obj.findall(
        './ObjectLocation[@elementtype="current location"]')
    if objectlocations is None:
        trace(1, '{}: No DateBegin for current location.', object_number)
        return False
    for ol in objectlocations:
        db = ol.find('./Date/DateBegin')
        if db is None or db.text is None:
            print(f'{object_number}: No DateBegin text')
            return False
        de = ol.find('./Date/DateEnd')
        if de is not None and de.text is not None:
            ol.set('elementtype', 'previous location')
            updated = True
    return updated


def main():
    global object_number, num_updated
    writeout(b'<?xml version="1.0"?>\n<Interchange>\n')
    for event, elem in ET.iterparse(infile):
        updated = False
        if elem.tag != 'Object':
            continue
        numelt = elem.find('./ObjectIdentity/Number')
        if numelt is not None:
            object_number = numelt.text
        else:
            object_number = 'Missing'
            trace(1, 'Missing "{}"', object_number)
        updated = one_object(elem)
        if updated:
            writeout(ET.tostring(elem, encoding='us-ascii'))
            num_updated += 1
        if _args.newline:
            writeout(b'\n')
        if _args.short:
            break
    writeout(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Modify the XML structure.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('-o', '--outfile', help='''
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
    assert sys.version_info >= (3, 6)
    object_number = None
    num_updated = 0
    _args = getargs()
    infile = open(_args.infile)
    outfile = None
    if _args.outfile:
        outfile = open(_args.outfile, 'wb')
    main()
    print (f'{num_updated} updated.')