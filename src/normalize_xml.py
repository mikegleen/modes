# -*- coding: utf-8 -*-
"""
Remove leading and trailing whitespace from text and convert multiple
whitespace sequences to single spaces. Insert a line feed after every Object
element if option -n is specified.
"""

import argparse
import sys
# noinspection PyPep8Naming
from bs4 import BeautifulSoup as BS
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars


def main():
    nlines = 0
    outfile.write(b'<?xml version="1.0" encoding="ASCII"?>\n<Interchange>')
    if _args.newline:
        outfile.write(b'\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        elem.text = elem.tail = None
        for e in elem.iter():
            # print(f'{e.tag} "{e.text}" "{e.tail}"')
            if e.text:
                e.text = ' '.join(e.text.strip().split())
            if e.tail:
                e.tail = ' '.join(e.tail.strip().split())
        xml = ET.tostring(elem, encoding='us-ascii')
        if _args.pretty:
            pxml = BS(xml, 'xml').prettify('us-ascii')
            # prettify inserts '<?xml....' at the front. Remove it.
            pxml = pxml.split(b'\n', 1)[1]
            outfile.write(pxml)
        else:
            outfile.write(xml)
        nlines += 1
        if _args.newline:
            outfile.write(b'\n')
        if _args.short:
            break
        elem.clear()
    outfile.write(b'</Interchange>')
    if _args.verbose >= 1:
        s = 's' if nlines > 1 else ''
        print(f'End normalize_xml. {nlines} object{s} written.')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Modify the XML structure. Remove leading and trailing spaces and
        convert multiple spaces to single spaces. The output encoding is
        US-ASCII. The input encoding defaults to UTF-8 by may be changed.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-e', '--encoding', default='utf-8', help='''
        Set the input encoding.
        ''')
    parser.add_argument('-n', '--newline', action='store_true', help='''
        If set, add a newline character at the end of each object element.
        ''')
    parser.add_argument('-p', '--pretty', action='store_true', help='''
        Prettyprint the output. This option implies --newline.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    if args.pretty:
        args.newline = True
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    _args = getargs()
    infile = open(_args.infile, encoding=_args.encoding)
    outfile = open(_args.outfile, 'wb')
    main()
