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
from utl.normalize import normalize_id, sphinxify
from utl.normalize import if_not_sphinx


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def nextobj(pnum: int, iterparser):
    """

    :param pnum: Either 1 or 2 indicating which iterparser has ben passed
    :param iterparser: Either file 1 or file 2 iterparser
    :return: a tuple of:
        the object parsed,
        the accession number,
        the normalized accession number,
        the output of ET.tostring(obj)
    """
    objectlevel = 0
    while True:
        try:
            event, obj = next(iterparser)
        except StopIteration:
            trace(5, 'End of file {}', pnum)
            return None, None, None, None
        if event == 'start':
            if obj.tag == config.record_tag:
                objectlevel += 1
            continue
        # It's an "end" event.
        if obj.tag != config.record_tag:
            continue
        objectlevel -= 1
        if objectlevel:
            continue  # It's not a top level Object.
        idelem = obj.find(config.record_id_xpath)
        idnum = idelem.text if idelem is not None else None
        nidnum = normalize_id(idnum)
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
    global objcount, deleted, added, replaced, written, skipped
    ip1 = ET.iterparse(infile1, events=('start', 'end'))
    ip2 = ET.iterparse(infile2, events=('start', 'end'))
    obj1, id1, nid1, objstr1 = nextobj(1, ip1)
    obj2, id2, nid2, objstr2 = nextobj(2, ip2)
    #
    #   Write output head
    #
    declaration = f'<?xml version="1.0" encoding="{_args.encoding}"?>\n'
    if _args.outfile:
        outfile.write(bytes(declaration, encoding=_args.encoding))
        outfile.write(b'<Interchange>\n')
    if _args.outorig:
        outorig.write(bytes(declaration, encoding=_args.encoding))
        outorig.write(b'<Interchange>\n')
    #
    #   Main Loop
    #
    while True:
        if nid2 is None:
            # Any objects left in infile2 are deleted
            if obj1 is None:
                break
            obj1.clear()
            trace(2, "Deleting object at end: {}", id1)
            obj1, id1, nid1, objstr1 = nextobj(1, ip1)
            deleted += 1
            continue
        if nid1 is None:
            # The objects in infile2 are new. Write them all
            written += 1
            added += 1
            trace(2, "Write new element at end {}", id2)
            outfile.write(objstr2)
            obj2.clear()
            obj2, id2, nid2, objstr2 = nextobj(2, ip2)
            continue
        if nid1 == nid2:
            if objstr1 != objstr2:
                trace(3, "Write changed element {}", id2)
                written += 1
                replaced += 1
                if _args.outfile:
                    outfile.write(objstr2)
                if _args.outorig:
                    outorig.write(objstr1)
            else:
                skipped += 1
                trace(4, "Skip unchanged {}", id1)
            obj1.clear()
            obj1, id1, nid1, objstr1 = nextobj(1, ip1)
            obj2.clear()
            obj2, id2, nid2, objstr2 = nextobj(2, ip2)
            continue
        if nid1 < nid2:
            # The old object has been deleted
            trace(2, "Deleting object: {}", id1)
            deleted += 1
            obj1.clear()
            obj1, id1, nid1, objstr1 = nextobj(1, ip1)
            continue
        # nid2 < nid1
        # A new object has been inserted.
        trace(2, "Write new element {}", id2)
        added += 1
        written += 1
        if _args.outfile:
            outfile.write(objstr2)
        obj2.clear()
        obj2, id2, nid2, objstr2 = nextobj(2, ip2)

    if _args.outfile:
        outfile.write(b'</Interchange>')
    if _args.outorig:
        outorig.write(b'</Interchange>')


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
    parser.add_argument('-e', '--encoding', default='utf-8', help=
                        '''Set the output encoding.''' +
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
    deleted = added = replaced = written = skipped = 0
    oldid = [None, '', '']
    basename = os.path.basename(sys.argv[0])
    trace(1, 'Begin {}', basename.split(".")[0], color=Fore.GREEN)
    infile1 = open(_args.infile1)
    infile2 = open(_args.infile2)
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
