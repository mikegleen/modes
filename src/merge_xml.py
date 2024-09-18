# -*- coding: utf-8 -*-
"""
    Merge two XML files.
"""
import argparse
from inspect import getframeinfo, stack
import os.path
import sys
import time
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from colorama import Fore, Style

from utl.cfgutil import Config
from utl.normalize import normalize_id


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
        idelem = oldobject.find(cfg.record_id_xpath)
        idnum = idelem.text if idelem is not None else None
        if not idnum:
            raise ValueError('Empty accession ID; aborting. Check output file for last'
                             ' good record.')
        des = oldobject.find('Identification/BriefDescription')
        des = des.text if des is not None else "***Missing BriefDescription***"
        nidnum = normalize_id(idnum)
        if nidnum in iddict:
            print(f'Duplicate ID: original: iddict[{nidnum}] = {idnum}, {des=}')
            print('Aborting.')
            sys.exit(1)
        iddict[nidnum] = idnum
        trace(2, 'Creating iddict[{}] = {}, des = {}', nidnum, idnum, des)
        outfile.write(ET.tostring(oldobject, encoding=_args.encoding))
        written += 1
        oldobject.clear()
    return written


def s(i: int):
    return '' if i == 1 else 's'


def main():
    t1 = time.perf_counter()
    declaration = f'<?xml version="1.0" encoding="{_args.encoding}"?>\n'
    outfile.write(bytes(declaration, encoding=_args.encoding))
    outfile.write(b'<Interchange>\n')
    total = 0
    for nfile, filename in enumerate(_args.infile, start=1):
        infile = open(filename)
        count = onefile(infile)
        infile.close()
        print(f'{count} object{s(count)} from file {nfile}: {filename}')
        total += count

    outfile.write(b'</Interchange>')
    elapsed = time.perf_counter() - t1
    print(f'{total} objects written in {elapsed:.3f} seconds to {_args.outfile}.')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Merge two XML Object files. Append the second file to the end of the
        first.
        ''')
    parser.add_argument('-i', '--infile', action='append', help='''
        The input XML files. You may specify multiple ``-i`` parameters. ''')
    parser.add_argument('-o', '--outfile', help='''
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
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs()
    trace(1, "Begin merge_xml.", color=Fore.GREEN)
    object_number = ''
    iddict = {}
    cfg = Config()
    outfile = open(_args.outfile, 'wb')
    main()
    trace(1, f'End merge_xml', color=Fore.GREEN)
