# -*- coding: utf-8 -*-
"""
    Output selected Object elements based on the YAML configuration file or
    command-line parameters.

"""
import argparse
import os.path
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfg import DEFAULT_MDA_CODE
from utl.cfgutil import Config
from utl.cfgutil import expand_idnum
from utl.readers import read_include_dict
from utl.excel_cols import col2num
from utl.normalize import normalize_id, sphinxify
from utl.normalize import if_not_sphinx


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def main():
    global objcount, selcount
    if not _args.directory:
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
        idelem = oldobject.find(config.record_id_xpath)
        idnum = idelem.text if idelem is not None else None
        if _args.normalize:
            idnum = normalize_id(idnum)
        selected = config.select(oldobject, includes, _args.exclude)
        objcount += 1
        if selected:
            selcount += 1
            outstring = ET.tostring(oldobject, encoding=_args.encoding)
            if _args.directory:
                objfilename = os.path.join(_args.outfile, idnum + '.xml')
                objfile = open(objfilename, 'wb')
                objfile.write(outstring)
                objfile.close()
            else:
                outfile.write(outstring)
        oldobject.clear()
        if _args.short:
            break
    if not _args.directory:
        outfile.write(b'</Interchange>')


def getparser():
    parser = argparse.ArgumentParser(description=sphinxify('''
        Copy a selected set of objects to a new XML file based on the config
        and/or a CSV/XLSX file giving explicit accessions numbers to include or
        exclude. Alternatively, one or more accession numbers may be specified
        with the --object parameter. If none of the parameters is given, the
        entire file is copied, possibly reformatting the text and converting
        ASCII to UTF-8.''', calledfromsphinx))
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-c', '--cfgfile', help='''
        The config file describing the Object elements to include in the
        output''')
    parser.add_argument('-d', '--directory', action='store_true',
                        help=sphinxify('''
        The output file is a directory. Create files in the directory,
        one per object in the XML file. The directory must be empty (but
        see --force).''', calledfromsphinx))
    parser.add_argument('-e', '--encoding', default='utf-8', help='''
        Set the output encoding. The default is "utf-8".
        ''')
    parser.add_argument('-f', '--force', action='store_true',
                        help=sphinxify('''
        Allow output to a directory that is not empty.
        ''', calledfromsphinx))
    parser.add_argument('--include', required=False, help='''
        A CSV file specifying the accession numbers of records to process.
        If omitted, all records will be processed based on configuration
        statements.''')
    parser.add_argument('--include_column', required=False, type=str,
                        default='0', help='''
        The column number containing the accession number in the file
        specified by the --include option. The default is 0, the first column.
         The column can be a number or a spreadsheet-style letter.''')
    parser.add_argument('--include_skip', type=int, default=0, help='''
        The number of rows to skip at the front of the include file. The
        default is 0.
        ''')
    parser.add_argument('-j', '--object', required=False, help='''
        Specify one or more objects to copy. Multiple objects may be specified
        using accession number expansion. See the Data Formats section of
        the Sphinx-formatted documentation.''')
    parser.add_argument('--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code, used in normalizing the accession number.''' +
                        if_not_sphinx(f''' The default is "{DEFAULT_MDA_CODE}".
                        ''', calledfromsphinx))
    parser.add_argument('-n', '--normalize', action='store_true', help='''
        Noramlize the accession number written to the CSV file or used to
        create the output filename.
        ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-x', '--exclude', action='store_true', help='''
        Treat the include list as an exclude list.''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    args.include_column = col2num(args.include_column)
    return args


calledfromsphinx = True
if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    calledfromsphinx = False
    objcount = selcount = 0
    object_number = ''
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    infile = open(_args.infile)
    if _args.directory:
        outfile = _args.outfile
        ld = os.listdir(outfile)
        if ld and not _args.force:
            print(f'Directory {outfile} is not empty. Exiting.')
            sys.exit()
    else:
        outfile = open(_args.outfile, 'wb')
    if _args.cfgfile:
        cfgfile = open(_args.cfgfile)
    else:
        cfgfile = None
    config = Config(cfgfile, mdacode=_args.mdacode, dump=_args.verbose >= 2)
    if _args.object:
        expanded = [normalize_id(obj) for obj in expand_idnum(_args.object)]
        includeset = set(expanded)  # JB001-002 -> JB001, JB002
        includes = dict.fromkeys(includeset)
    else:
        includes = read_include_dict(_args.include, _args.include_column,
                                     _args.include_skip, _args.verbose)
    main()
    basename = os.path.basename(sys.argv[0])
    trace(1, f'{selcount} object{"" if selcount == 1 else "s"} selected from {objcount}.')
    trace(1, f'End {basename.split(".")[0]}')
