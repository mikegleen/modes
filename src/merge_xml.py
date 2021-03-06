# -*- coding: utf-8 -*-
"""
    Output selected Object elements based on the YAML configuration file.

"""
import argparse
import os.path
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def onefile(infile):
    written = 0
    objectlevel = 0
    for event, oldobject in ET.iterparse(infile, events=('start', 'end')):
        if event == 'start':
            if oldobject.tag == 'Object':
                objectlevel += 1
            continue
        # It's an "end" event.
        if oldobject.tag != 'Object':
            continue
        objectlevel -= 1
        if objectlevel:
            continue  # It's not a top level Object.
        outfile.write(ET.tostring(oldobject, encoding=_args.encoding))
        written += 1
        oldobject.clear()
    return written


def main():
    declaration = f'<?xml version="1.0" encoding="{_args.encoding}"?>\n'
    outfile.write(bytes(declaration, encoding=_args.encoding))
    outfile.write(b'<Interchange>\n')
    infile = open(_args.infile)
    count1 = onefile(infile)
    infile.close()
    infile = open(_args.mergefile)
    count2 = onefile(infile)
    outfile.write(b'</Interchange>')
    print(f'{count1} objects from file 1')
    print(f'{count2} objects from file 2')
    print(f'{count1 + count2} objects written')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Merge two XML Object files.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('mergefile', help='''
        The second input XML file.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-e', '--encoding', default='utf-8', help='''
        Set the output encoding. The default is "utf-8".
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    object_number = ''
    _args = getargs()
    outfile = open(_args.outfile, 'wb')
    main()
    basename = os.path.basename(sys.argv[0])
    print(f'End {basename.split(".")[0]}')

