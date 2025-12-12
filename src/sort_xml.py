# -*- coding: utf-8 -*-
"""

Create output file sorted by object ID if the output file is specified.

Report and discard any records with duplicate accession numbers.
"""

import argparse
from inspect import getframeinfo, stack
import os.path
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars
# import tracemalloc
import psutil

from utl.cfg import DEFAULT_MDA_CODE
from utl.normalize import normalize_id, denormalize_id
from utl.readers import row_dict_reader

from colorama import Fore, Style


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if _args.verbose > 1:
            caller = getframeinfo(stack()[1][0])
            print(f'{os.path.basename(caller.filename)} line {caller.lineno}: ', end='')
        if color:
            if len(args) == 0:
                print(f'{color}{template}{Style.RESET_ALL}')
            else:
                print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            if len(args) == 0:
                print(template)
            else:
                print(template.format(*args))


def read_renumber():
    renum_dict = dict()
    newnum_set = set()
    for row in row_dict_reader(_args.renumber, verbos=_args.verbose):
        oldnum = normalize_id(row['OldSerial'], _args.mdacode)
        newnum = normalize_id(row['NewSerial'], _args.mdacode)
        if oldnum in renum_dict:
            trace(0, 'Duplicate OldNumber in CSV: {}', row['OldSerial'],
                  color=Fore.RED)
            sys.exit(1)
        if newnum in newnum_set:
            trace(0, 'Duplicate NewNumber in CSV: {}', row['NewSerial'],
                  color=Fore.RED)
            sys.exit(1)
        renum_dict[oldnum] = newnum
        newnum_set.add(newnum)
    return renum_dict, newnum_set


def onefile(ifile, ofile) -> int:
    if _args.dryrun:
        print(f'{ifile=}, {ofile=}')
        return 0
    objdict = {}
    outfile = open(ofile, 'wb')
    infile = open(ifile, encoding=_args.encoding)
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
            if _args.nostrict:
                trace(1, f'**** seq {seq}, ID {num} is a duplicate, '
                         f'ignored.', color=Fore.LIGHTYELLOW_EX)
                continue
            trace(0, f'**** seq {seq}, ID {num} is a duplicate, aborting. Set '
                  f'--nostrict to allow duplicates which will be discarded.',
                  color=Fore.RED)
            sys.exit(1)
        objdict[numn] = elem
    dupfound = False
    for newnum in newnumset:
        if newnum in objdict:
            dupfound = True
            trace(1, 'Error: New number {} already exists.',
                  denormalize_id(newnum), color=Fore.RED)
    if dupfound:
        sys.exit(1)
    for oldnum, newnum in renumdict.items():
        elem = objdict[oldnum]
        numelem = elem.find('./ObjectIdentity/Number')
        numelem.text = denormalize_id(newnum)
        repro = elem.find('.Reproduction/Filename')
        if repro is not None:
            repro.text = f'{denormalize_id(newnum)}.jpg'
        del objdict[oldnum]
        objdict[newnum] = elem
    for numn in sorted(objdict):
        outfile.write(ET.tostring(objdict[numn], encoding='utf-8').strip())
    outfile.write(b'\n</Interchange>')
    return len(objdict)


def sort_files_in_folder():
    path_head = _args.directory
    files = [f for f in os.listdir(path_head)
             if os.path.isfile(os.path.join(path_head, f)) and f.endswith('.xml')]
    for filename in files:
        if '_sorted' in filename:
            continue
        root, ext = os.path.splitext(filename)
        infilepath = os.path.join(path_head, filename)
        outfilename = root + '_sorted' + ext
        if outfilename in files:
            continue
        outfilepath = os.path.join(path_head, outfilename)
        numobjs = onefile(infilepath, outfilepath)
        trace(1, '{} objects written to {}.', numobjs, outfilepath)
    return


def main():
    if _args.directory is not None:
        sort_files_in_folder()
    else:
        numobjs = onefile(_args.infile, _args.outfile)
        trace(1, f'End sort_xml. {numobjs} objects written.',
              color=Fore.GREEN)


def getparser():
    parser = argparse.ArgumentParser(description='''
        Create an output file sorted by Object ID.
        ''')
    megroup = parser.add_mutually_exclusive_group()
    megroup.add_argument('-i', '--infile', help='''
        The XML file saved from Modes.''')
    megroup.add_argument('-d', '--directory', help='''
        The directory containing files to be sorted. A sorted file
        will be created in the same directory with "_sorted" inserted into
        the name before the extension.''')
    parser.add_argument('-o', '--outfile', help='''
        The sorted XML file. Only allowed (and required) if --infile is specified.''')
    parser.add_argument('--dryrun', action='store_true', help='''
        Only print the names of files to be sorted.''')
    parser.add_argument('--encoding', default='utf-8', help='''
        Set the input encoding. Default is utf-8. Output is always utf-8.
        ''')
    parser.add_argument('-m', '--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code, used in normalizing the accession number.
        The default is "{DEFAULT_MDA_CODE}".
        ''')
    parser.add_argument('-n', '--nostrict', action='store_true', help='''
        Allow duplicate accession numbers. If not set, a duplicate accession
        number will cause the program to abort.
        ''')
    parser.add_argument('-r', '--renumber', help=f'''
        A CSV file containing two columns with headings OldSerial and NewSerial.
        The accession numbers will be changed accordingly. The program will abort
        if you try to  create a duplicate accession number.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if args.directory and args.outfile:
        raise ValueError('You cannot specify an output file if the input is '
                         'a directory.')
    if args.infile and not args.outfile:
        raise ValueError('You must specify an output file if the input file is '
                         'specified.')
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 14)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    trace(1, 'Begin sort_xml.', color=Fore.GREEN)
    renumdict, newnumset = read_renumber()
    main()
    process = psutil.Process()
    print(f'Max memory usage (bytes): {process.memory_info().rss:,}')
