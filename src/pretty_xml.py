# -*- coding: utf-8 -*-
"""
For an XML file in a pre-defined location, create a pretty version in a
subfolder named "pretty" with "pretty" embedded in the filename.
"""

import argparse
import os.path
import sys
import xml.dom.minidom as minidom
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars

ROOTDIR = '/Users/mlg/pyprj/hrm/modes'
INDIR = ROOTDIR + '/results/xml'
PRETTYDIR = INDIR + '/pretty'


def getfiles():
    """

    :return: A tuple of the input file and output file. If necessary, create
    the output subdirectory "pretty".
    """
    os.makedirs(PRETTYDIR, exist_ok=True)
    filename: str = _args.infile
    inputfile = open(os.path.join(INDIR, filename))
    print(f'Reading file {inputfile.name}')

    # 2021-04-30_children.xml -> 2021-04-30_pretty_children.xml
    parts = filename.split('_')
    if len(parts) == 1:
        raise ValueError('Filename must be of format yyyy-mm-dd_name.xml')
    parts[0] += '_pretty'
    prettyname = '_'.join(parts)
    prettyfile = open(PRETTYDIR + '/' + prettyname, 'wb')
    print(f'Creating file: {prettyfile.name}')
    return inputfile, prettyfile


def main():
    nlines = 0
    declaration = ('<?xml version="1.0" encoding="'
                   f'{_args.output_encoding}"?>\n<Interchange>')
    outfile.write(bytes(declaration, _args.output_encoding))
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
        The input XML file is assumed to be in {INDIR}. The output directory
        will be {PRETTYDIR}. The output file will have "pretty" inserted after
        the leading date.''')
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
    assert sys.version_info >= (3, 9)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs()
    infile, outfile = getfiles()
    main()
