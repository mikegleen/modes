# -*- coding: utf-8 -*-
"""

Create output file sorted by object ID.
"""

import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars

from utl.normalize_obj_id import normalize


def main():
    objdict = {}
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    seq = 0
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        seq += 1
        num = elem.find('./ObjectIdentity/Number').text
        num = normalize(num)
        if num in objdict:
            print (f'seq {seq}, ID {num} is a duplicate, ignored.')
            continue
        objdict[num] = ET.tostring(elem, encoding='us-ascii').strip()
    for num in sorted(objdict):
        outfile.write(objdict[num])
        outfile.write(b'\n')
    outfile.write(b'</Interchange>')


if __name__ == '__main__':
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    infile = open(sys.argv[1])
    outfile = open(sys.argv[2], 'wb')
    main()
