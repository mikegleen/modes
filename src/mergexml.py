# -*- coding: utf-8 -*-
"""
    Merge two Modes XML Object files.

    It is required that input files are in order according to normalized
    accession numbers.

    Note that this script has been tested against a "normal" Modes XML Object
    file. It is explicitly not guaranteed to work with arbitrary XML files.
    For example, multiple attributes are allowed on elements and they can be
    in any order. This script may issue false "changed" output in those cases.

    Trace levels:

    #. Summary info
    #. Inserted and deleted objects
    #. Changed objects
    #. Unchanged objects
    #. Details for debugging
"""
import argparse
import os.path
import sys
import time
from colorama import Fore, Style
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfg import DEFAULT_MDA_CODE
from utl.cfgutil import Config
from utl.normalize import sphinxify, if_not_sphinx
from utl.readers import object_reader


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def nextobj(pnum: int, reader: object_reader):
    """

    :param pnum: Either 1 or 2 indicating which object_reader has ben passed
    :param reader: Either file 1 or file 2 object_reader
    :return: a tuple of:
        the object parsed,
        the accession number,
        the normalized accession number,
        the output of ET.tostring(obj)
    """

    idnum, nidnum, obj = next(reader)
    objstr = ET.tostring(obj)
    trace(5, 'File {} {}', pnum, nidnum)
    if nidnum <= oldid[pnum]:
        trace(0, "Objects out of order in file {}. Old ID = {}, "
                 "New ID = {}", pnum, oldid[pnum], nidnum,
              color=Fore.RED)
        sys.exit(-1)
    objcount[pnum] += 1
    oldid[pnum] = nidnum
    return obj, idnum, nidnum, objstr


def main():
    global objcount, written
    reader1 = object_reader(_args.infile1, normalize=True, verbos=_args.verbos)
    reader2 = object_reader(_args.infile2, normalize=True, verbos=_args.verbos)
    obj1, id1, nid1, objstr1 = nextobj(1, reader1)
    obj2, id2, nid2, objstr2 = nextobj(2, reader2)
    #
    #   Write output head
    #
    declaration = f'<?xml version="1.0" encoding="{_args.encoding}"?>\n'
    if _args.outfile:
        outfile.write(bytes(declaration, encoding=_args.encoding))
        outfile.write(b'<Interchange>\n')
    #
    #   Main Loop
    #
    while True:
        if nid2 is None:
            if obj1 is None:
                break
            written += 1
            if _args.outfile:
                outfile.write(objstr1)
            obj1.clear()
            obj1, id1, nid1, objstr1 = nextobj(1, reader1)
            trace(2, "Write file1 element at end: {}", nid1)
            continue
        if nid1 is None:
            # The objects in infile2 are new. Write them all
            written += 1
            trace(2, "Write file2 element at end: {}", nid2)
            if _args.outfile:
                outfile.write(objstr2)
            obj2.clear()
            obj2, id2, nid2, objstr2 = nextobj(2, reader2)
            continue
        if nid1 == nid2:
            if _args.allow_replace:
                written += 1
                trace(2, "Duplicate found. Write file2 element: {}", nid2)
                if _args.outfile:
                    outfile.write(objstr2)
                obj1.clear()
                obj2.clear()
                obj1, id1, nid1, objstr1 = nextobj(1, reader1)
                obj2, id2, nid2, objstr2 = nextobj(2, reader2)
                continue
            trace(1, "Aborting due to duplicate object {}", id1, color=Fore.RED)
            sys.exit(1)
        if nid1 < nid2:
            written += 1
            if _args.outfile:
                outfile.write(objstr1)
            obj1.clear()
            obj1, id1, nid1, objstr1 = nextobj(1, reader1)
            trace(2, "Write file1 element: {}", nid1)
            continue
        # nid2 < nid1
        trace(2, "Write file2 element {}", id2)
        written += 1
        if _args.outfile:
            outfile.write(objstr2)
        obj2.clear()
        obj2, id2, nid2, objstr2 = nextobj(2, reader2)

    if _args.outfile:
        outfile.write(b'</Interchange>')


def getparser():
    parser = argparse.ArgumentParser(description=sphinxify('''
        Compare two Modes XML Object files and output just the elements that
        have changed or been added. If an element has been deleted, the accession
        number is reported.
        ''', calledfromsphinx))
    parser.add_argument('infile1', help='''
        The old XML file''')
    parser.add_argument('infile2', help='''
        The updated XML file.''')
    parser.add_argument('-c', '--config', help=sphinxify('''
        Optionally specify a YAML configuration file to allow specification
        of ``record_tag`` and ``record_id_xpath`` statements.''', calledfromsphinx))
    parser.add_argument('-e', '--encoding', default='utf-8',
                        help='''Set the output encoding.''' +
                        if_not_sphinx(''' The default is "utf-8".
                        ''', calledfromsphinx))
    parser.add_argument('--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code, used in normalizing the accession number.''' +
                        if_not_sphinx(f''' The default is "{DEFAULT_MDA_CODE}".
                        ''', calledfromsphinx))
    parser.add_argument('-o', '--outfile', help=sphinxify('''
        The XML file containing the changed or added Object elements.
        If this parameter is not specified, only messages will be displayed
        and no output will be written.''', calledfromsphinx))
    parser.add_argument('-r', '--allow_replace', action='store_true', help=sphinxify('''
        If set, records in file 2 will replace records from file 1. If not set, the program
        will abort. ''' + if_not_sphinx('Default: False', calledfromsphinx), calledfromsphinx))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if not args.outfile:
        print('Dry run. No output written.')
    return args


def s(i: int):
    return '' if i == 1 else 's'


calledfromsphinx = True
if __name__ == '__main__':
    assert sys.version_info >= (3, 11)
    t1 = time.perf_counter()
    calledfromsphinx = False
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    #
    # Global variables
    #
    objcount = [None, 0, 0]
    written = 0
    oldid = [None, '', '']
    basename = os.path.basename(sys.argv[0])
    trace(1, 'Begin {}', basename.split(".")[0], color=Fore.GREEN)
    if _args.outfile:
        outfile = open(_args.outfile, 'wb')
    config = Config(_args.config, mdacode=_args.mdacode, dump=_args.verbose >= 2)
    main()
    trace(1, '{} object{} in file 1: {}', objcount[1], s(objcount[1]), _args.infile1)
    trace(1, '{} object{} in file 2: {}', objcount[2], s(objcount[2]), _args.infile2)
    if _args.outfile:
        trace(1, '{} object{} written to {}.', written, s(written), _args.outfile)
    elapsed = time.perf_counter() - t1
    trace(1, 'End {}. Elapsed: {:5.3f} seconds.', basename.split(".")[0],
          elapsed, color=Fore.GREEN)
