# -*- coding: utf-8 -*-
"""

Create output file sorted by object ID if the output file is specified.

Report and discard any records with duplicate accession numbers.
"""

import argparse
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars

from utl.normalize import normalize_id, DEFAULT_MDA_CODE


def main():
    objdict = {}
    if outfile:
        outfile.write(b'<?xml version="1.0" encoding="utf-8"?><Interchange>\n')
    seq = 0
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        seq += 1
        num = elem.find('./ObjectIdentity/Number').text
        numn = normalize_id(num, _args.mdacode)
        if _args.verbose > 1:
            print(f'{seq:4}. {num}')
        if numn in objdict:
            print(f'**** seq {seq}, ID {num} is a duplicate, ignored.')
            continue
        objdict[numn] = ET.tostring(elem, encoding='utf-8').strip()
    if not outfile:
        return
    for numn in sorted(objdict):
        outfile.write(objdict[numn])
        outfile.write(b'\n')
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Create an output file sorted by Object ID.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('-o', '--outfile', help='''
        The sorted XML file.''')
    parser.add_argument('--encoding', default='utf-8', help='''
        Set the input encoding. Default is utf-8. Output is always utf-8.
        ''')
    parser.add_argument('-m', '--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code, used in normalizing the accession number.
        The default is "{DEFAULT_MDA_CODE}".
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 7)
    _args = getargs()
    infile = open(_args.infile, encoding=_args.encoding)
    outfile = open(_args.outfile, 'wb') if _args.outfile else None
    main()
