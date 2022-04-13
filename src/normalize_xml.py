# -*- coding: utf-8 -*-
"""
Remove leading and trailing whitespace from text and convert multiple
whitespace sequences to single spaces. Insert a line feed after every Object
element if option -n is specified.
"""

import argparse
import sys
import time
import xml.dom.minidom as minidom
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars


def main():
    nlines = 0
    t1 = time.perf_counter()
    declaration = ('<?xml version="1.0" encoding="'
                   f'{_args.output_encoding}"?>\n<Interchange>')
    outfile.write(bytes(declaration, _args.output_encoding))
    if _args.newline or _args.pretty:
        outfile.write(b'\n')
    objectlevel = 0
    for event, elem in ET.iterparse(infile, events=('start', 'end')):
        if event == 'start':
            if elem.tag == 'Object':
                objectlevel += 1
            continue
        # It's an "end" event.
        if elem.tag != 'Object':
            continue
        objectlevel -= 1
        if objectlevel:
            continue  # It's not a top level Object.
        elem.text = elem.tail = None
        for e in elem.iter():
            # print(f'{e.tag} "{e.text}" "{e.tail}"')
            if e.text:
                e.text = ' '.join(e.text.strip().split())
            if e.tail:
                e.tail = ' '.join(e.tail.strip().split())
        xmlstring = ET.tostring(elem, encoding=_args.output_encoding,
                                xml_declaration=False)
        if _args.pretty:
            reparsed = minidom.parseString(xmlstring)
            prettyxml = reparsed.toprettyxml(indent="\t",
                                             encoding=_args.output_encoding)
            # toprettyxml inserts '<?xml....' at the front. Remove it.
            prettyxml = prettyxml.split(b'\n', 1)[1]
            # minidom converts '"' to '&quot' so let elementtree redo it
            etparsed = ET.fromstring(prettyxml)
            xmlstring = ET.tostring(etparsed, encoding=_args.output_encoding,
                                    xml_declaration=False)
        outfile.write(xmlstring)
        nlines += 1
        if _args.newline:
            outfile.write(b'\n')
        if _args.short:
            break
        elem.clear()
    outfile.write(b'</Interchange>')
    if _args.verbose >= 1:
        elapsed = time.perf_counter() - t1
        s = 's' if nlines > 1 else ''
        print(f'End normalize_xml. {nlines} object{s} written in {elapsed:.3f} seconds')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Modify the XML structure. Remove leading and trailing spaces and
        convert multiple spaces to single spaces.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-e', '--input_encoding', default=None, help='''
        Set the input encoding. The encoding defaults to UTF-8. If set, you
        must also set --output_encoding.
        ''')
    parser.add_argument('-g', '--output_encoding', default=None, help='''
        Set the output encoding. The encoding defaults to UTF-8. If set, you
        must also set --input_encoding.
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
    e = args.input_encoding
    g = args.output_encoding
    if (e and not g) or (g and not e):
        raise ValueError(
            'Both input and output encoding must be specified.')
    elif not e:
        args.input_encoding = args.output_encoding = 'UTF-8'
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    if _args.infile == _args.outfile:
        print("Input is the same as output. Aborting.")
        sys.exit(1)
    infile = open(_args.infile, encoding=_args.input_encoding)
    outfile = open(_args.outfile, 'wb')
    main()
