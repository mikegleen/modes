# -*- coding: utf-8 -*-
"""
Remove leading and trailing whitespace from text and convert multiple
whitespace sequences to single spaces. Insert a line feed after every Object
element.
"""

import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def main():
    outfile.write(b'<?xml version="1.0"?><Interchange>')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        for e in elem.iter():
            if e.text:
                e.text = ' '.join(e.text.strip().split())
            if e.tail:
                e.tail = ' '.join(e.tail.strip().split())
        outfile.write(ET.tostring(elem, encoding='us-ascii'))
        outfile.write(b'\n')
    outfile.write(b'</Interchange>')

if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    infile = open(sys.argv[1])
    outfile = open(sys.argv[2], 'wb')
    main()
