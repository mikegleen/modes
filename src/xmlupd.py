"""
    Apply a detail file to a master file creating a new master file. The detail file
    contains either updated object records or new object records. There is no mechanism
    to delete records from the master file. Use ``update_from_csv.py`` to delete records.

    It is required that input files are in order according to normalized
    accession numbers.

    Trace levels:

    #. Summary info
    #. Inserted objects
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

from utl import readers
from utl.cfgutil import Config, DEFAULT_MDA_CODE
from utl.normalize import if_not_sphinx, sphinxify


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def nextobj(pnum: int, objectreader):
    """

    :param pnum: Either 1 or 2 indicating which object reader has ben passed
    :param objectreader: Either file 1 or file 2 object_reader
    :return: a tuple of:
        the object parsed,
        the accession number,
        the normalized accession number,
        the output of ET.tostring(obj)
    """

    while True:
        try:
            idnum, nidnum, obj = next(objectreader)
        except StopIteration:
            trace(5, 'End of file {}', pnum)
            return None, None, None, None
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
    config = Config(_args.config, mdacode=_args.mdacode, dump=_args.verbose >= 2)
    ip1 = readers.object_reader(_args.infile1, config=config, normalize=True,)
    ip2 = readers.object_reader(_args.infile2, config=config, normalize=True)
    obj1, id1, nid1, objstr1 = nextobj(1, ip1)
    obj2, id2, nid2, objstr2 = nextobj(2, ip2)
    #
    #   Write output head
    #
    declaration = f'<?xml version="1.0" encoding="{_args.encoding}"?>\n'
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
            # Any objects left in infile1 are copied to output
            if obj1 is None:
                break
            outfile.write(objstr1)
            written += 1
            obj1.clear()
            trace(2, "Writing object from master file at end: {}", id1)
            obj1, id1, nid1, objstr1 = nextobj(1, ip1)
        elif nid1 is None:
            # The objects in infile2 are new. Write them all
            written += 1
            added += 1
            trace(2, "Write new element at end {}", id2)
            outfile.write(objstr2)
            obj2.clear()
            obj2, id2, nid2, objstr2 = nextobj(2, ip2)
        elif nid1 == nid2:
            trace(3, "Write changed element {}", id2)
            written += 1
            replaced += 1
            outfile.write(objstr2)
            if _args.outorig:
                outorig.write(objstr1)
            obj1.clear()
            obj1, id1, nid1, objstr1 = nextobj(1, ip1)
            obj2.clear()
            obj2, id2, nid2, objstr2 = nextobj(2, ip2)
        elif nid1 < nid2:
            trace(2, "Keeping object: {}", id1)
            outfile.write(objstr1)
            written += 1
            obj1.clear()
            obj1, id1, nid1, objstr1 = nextobj(1, ip1)
        else:
            # nid2 < nid1
            # A new object has been inserted.
            trace(2, "Write new element {}", id2)
            added += 1
            written += 1
            outfile.write(objstr2)
            obj2.clear()
            obj2, id2, nid2, objstr2 = nextobj(2, ip2)

    outfile.write(b'</Interchange>')
    if _args.outorig:
        outorig.write(b'</Interchange>')


def getparser():
    parser = argparse.ArgumentParser(description=sphinxify('''
    Apply a detail file to a master file creating a new master file. The detail file
    contains either updated object records or new object records. There is no mechanism
    to delete records from the master file.
        ''', calledfromsphinx))
    parser.add_argument('infile1', help='''
        The old XML master file''')
    parser.add_argument('infile2', help='''
        The detail XML file.''')
    parser.add_argument('-c', '--config', help=sphinxify('''
        Optionally specify a YAML configuration file to allow specification
        of ``record_tag`` and ``record_id_xpath`` statements. The default is
        to conform to Modes format.
        ''', calledfromsphinx))
    parser.add_argument('-e', '--encoding', default='utf-8', help='''
                        Set the output encoding.''' +
                        if_not_sphinx(''' The default is "utf-8".
                        ''', calledfromsphinx))
    parser.add_argument('--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code, used in normalizing the accession number.''' +
                        if_not_sphinx(''' The default is "{DEFAULT_MDA_CODE}".
                        ''', calledfromsphinx))
    parser.add_argument('-o', '--outfile', required=True, help=sphinxify('''
        The updated XML master file containing the changed or added Object elements. Required.
        ''', calledfromsphinx))
    parser.add_argument('--outorig', help='''
        The XML file containing the Object elements from the old XML file
        if the element in the new file is different.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if not args.outfile and not args.outorig:
        print('Dry run. No output written')
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
    outfile = open(_args.outfile, 'wb')
    if _args.outorig:
        outorig = open(_args.outorig, 'wb')
    main()
    trace(1, '{} object{} in master file: {}', objcount[1], s(objcount[1]), _args.infile1)
    trace(1, '{} object{} in detail file: {}', objcount[2], s(objcount[2]), _args.infile2)
    trace(1, '{} object{} deleted.', deleted, s(deleted))
    trace(1, '{} object{} added.', added, s(added))
    trace(1, '{} object{} replaced.', replaced, s(replaced))
    trace(1, '{} object{} written to {}.', written, s(written), _args.outfile)
    if _args.outorig:
        trace(1, '{} object{} written to {}.', written, s(written), _args.outorig)
    elapsed = time.perf_counter() - t1
    trace(1, 'End {}. Elapsed: {:5.3f} seconds.', basename.split(".")[0],
          elapsed, color=Fore.GREEN)
