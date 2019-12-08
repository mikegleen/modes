# -*- coding: utf-8 -*-
"""
    Compare Production/Medium vs Description... medium
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


def one_object(obj):
    prod = obj.find('./Production')
    pm = prod.find('./Medium')
    if pm is None:
        print(object_number, "pm is none")
        return
    if pm.text is None:
        print(object_number, "pm.text is none")
        prod.remove(pm)
        return
    dm = obj.find('./Description/Material[Part="medium"]')
    if dm is None:
        print(object_number, "dm is none")
        return
    keys = dm.findall('./Keyword')
    if len(keys) == 0:
        print(object_number, "no keys found, adding a key")
        key = ET.Element('Keyword')
        key.text = pm.text
        dm.append(key)
        prod.remove(pm)
        return
    for key in keys:
        if key.text == pm.text:
            print(object_number, "key.text matches")
            prod.remove(pm)
            return
    for key in keys:
        print(object_number, f"key: '{key.text}'")
        if key.text is None or len(key.text) == 0:
            print(object_number, f"updating empty key with: {pm.text}")
            key.text = pm.text
            prod.remove(pm)
            return
    print(object_number, "no empty keys found, adding a key")
    key = ET.Element('Keyword')
    key.text = pm.text
    dm.append(key)
    prod.remove(pm)


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
