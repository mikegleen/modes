# -*- coding: utf-8 -*-
"""
    Output selected Object elements based on the YAML configuration file.

"""
import argparse
import os.path
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfgutil import Config, read_include_dict
from utl.cfgutil import expand_idnum
from utl.normalize import normalize_id, denormalize_id


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def main():
    global objcount, selcount
    declaration = f'<?xml version="1.0" encoding="{_args.encoding}"?>\n'
    outfile.write(bytes(declaration, encoding=_args.encoding))
    outfile.write(b'<Interchange>\n')
    objectlevel = 0
    for event, oldobject in ET.iterparse(infile, events=('start', 'end')):
        if event == 'start':
            if oldobject.tag == config.record_tag:
                objectlevel += 1
            continue
        # It's an "end" event.
        if oldobject.tag != config.record_tag:
            continue
        objectlevel -= 1
        if objectlevel:
            continue  # It's not a top level Object.
        selected = config.select(oldobject, includes, _args.exclude)
        objcount += 1
        if selected:
            selcount += 1
            outfile.write(ET.tostring(oldobject, encoding=_args.encoding))
        oldobject.clear()
        if _args.short:
            break
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Copy a selected set of objects to a new XML file based on the config
        and a CSV file giving explicit accessions numbers to include or
        exclude. If neither parameter is given, the entire file is copied,
        possibly reformatting the text and converting ASCII to UTF-8.''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-c', '--cfgfile', required=False, help='''
        The config file describing the Object elements to include in the
        output''')
    parser.add_argument('-e', '--encoding', default='utf-8', help='''
        Set the output encoding. The default is "utf-8".
        ''')
    parser.add_argument('--include', required=False, help='''
        A CSV file specifying the accession numbers of records to process.
        If omitted, all records will be processed based on configuration
        statements.''')
    parser.add_argument('--include_column', required=False, type=int,
                        default=0, help='''
        The column number containing the accession number in the file
        specified by the --select option. The default is 0, the first column.'''
                        )
    parser.add_argument('--include_skip', type=int, default=0, help='''
        The number of rows to skip at the front of the include file. The
        default is 0.
        ''')
    parser.add_argument('-j', '--object', required=False, help='''
        Specify a single object to copy. ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-x', '--exclude', action='store_true', help='''
        Treat the include list as an exclude list.''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    objcount = selcount = 0
    object_number = ''
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    if _args.cfgfile:
        cfgfile = open(_args.cfgfile)
    else:
        cfgfile = None
    config = Config(cfgfile, dump=_args.verbose >= 2)
    if _args.object:
        expanded = [normalize_id(obj) for obj in expand_idnum(_args.object)]
        includeset = set(expanded)  # JB001-002 -> JB001, JB002
        includes = dict.fromkeys(includeset)
    else:
        includes = read_include_dict(_args.include, _args.include_column,
                                     _args.include_skip, _args.verbose)
    main()
    basename = os.path.basename(sys.argv[0])
    print(f'{selcount} object{"" if selcount == 1 else "s"} selected from {objcount}.')
    print(f'End {basename.split(".")[0]}')
