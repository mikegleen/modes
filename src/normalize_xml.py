# -*- coding: utf-8 -*-
"""
Remove leading and trailing whitespace from text and convert multiple
whitespace sequences to single spaces. Insert a line feed after every Object
element if option -n is specified.
"""

import argparse
import sys
import xml.dom.minidom as minidom
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
        xmlstring = ET.tostring(elem, encoding='us-ascii')
        if _args.pretty:
            reparsed = minidom.parseString(xmlstring)
            prettyxmlstring = reparsed.toprettyxml(indent="\t", encoding='ascii')
            # toprettyxml inserts '<?xml....' at the front. Remove it.
            prettyxmlstring = prettyxmlstring.split(b'\n', 1)[1]
            outfile.write(prettyxmlstring)
        else:
            outfile.write(xmlstring)
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
        US-ASCII. The input encoding defaults to UTF-8 but may be changed.
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
        Prettyprint the output.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    targetversion = sys.version_info.major * 1000 + sys.version_info.minor
    if targetversion < 3007:
        raise ImportError('requires Python 3.7 or higher')
    _args = getargs()
    infile = open(_args.infile, encoding=_args.encoding)
    outfile = open(_args.outfile, 'wb')
    main()
