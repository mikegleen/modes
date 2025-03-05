# -*- coding: utf-8 -*-
"""
For an XML file in a pre-defined location, create a pretty version in a
subfolder named "pretty" with "pretty" embedded in the filename.

If an output file is named explicitly, bypass the default behavior and use the
input and output file paths given.
"""

import argparse
import sys
import xml.dom.minidom as minidom
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars

from utl.xmlutil import get_record_tag


def main():
    nlines = 0
    if is_template:
        declaration = '<templates application="Object">'
    else:
        declaration = ('<?xml version="1.0" encoding="'
                       f'{_args.output_encoding}"?>\n<Interchange>')
    outfile.write(bytes(declaration, _args.output_encoding))
    outfile.write(b'\n')
    objectlevel = 0

    for event, elem in ET.iterparse(infile, events=('start', 'end')):
        if event == 'start':
            if elem.tag == record_tag:
                objectlevel += 1
            continue
        # It's an "end" event.
        if elem.tag != record_tag:
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
        reparsed = minidom.parseString(xmlstring)
        prettyxml = reparsed.toprettyxml(indent="\t",
                                         encoding=_args.output_encoding)
        # toprettyxml inserts '<?xml....' at the front. Remove it.
        prettyxml = prettyxml.split(b'\n', 1)[1]
        outfile.write(prettyxml)
        nlines += 1
        if _args.short:
            break
        elem.clear()
    if is_template:
        outfile.write(b'</templates>')
    else:
        outfile.write(b'</Interchange>')
    if _args.verbose >= 1:
        s = 's' if nlines > 1 else ''
        print(f'End pretty_xml. {nlines} object{s} written.')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Modify the XML structure. Remove leading and trailing spaces and
        convert multiple spaces to single spaces.
        ''')
    parser.add_argument('infile', help=f'''
        The path to the input XML file.''')
    parser.add_argument('outfile', help=f'''
        Specify the output pretty file.
    ''')
    parser.add_argument('-e', '--input_encoding', default=None, help='''
        Set the input encoding. The encoding defaults to UTF-8. If set, you
        must also set --output_encoding.
        ''')
    parser.add_argument('-g', '--output_encoding', default=None, help='''
        Set the output encoding. The encoding defaults to UTF-8. If set, you
        must also set --input_encoding.
        ''')
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
    assert sys.version_info >= (3, 13)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs()
    record_tag = get_record_tag(_args.infile)
    is_template = True if record_tag == 'template' else False
    print(f'{record_tag=}')
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
