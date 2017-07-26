# -*- coding: utf-8 -*-
"""
    If an Object is missing its <Number> tag, insert a sequential X1..Xn.
"""

import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def handle_object(elem):
    global objnum
    idelem = elem.find('./ObjectIdentity/Number')
    if idelem is None:
        idelem = elem.find('./ObjectIdentity')
        objnum += 1
        numelem = ET.SubElement(idelem, 'Number')
        numelem.text = f'X{objnum}'
    outfile.write(ET.tostring(elem, encoding='us-ascii'))
    # outfile.write(b'\n')


def main():
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        handle_object(elem)
    outfile.write(b'</Interchange>')

if __name__ == '__main__':
    objnum = 0
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    infile = open(sys.argv[1])
    outfile = open(sys.argv[2], 'wb')
    main()
