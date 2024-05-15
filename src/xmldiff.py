# -*- coding: utf-8 -*-
"""
    Compare two Modes XML Object files and output only the Object elements that
    have changed or been added. These "diff" file can then be used to update
    Modes without having to update all objects. This preserves the change
    history metadata.

    It is required that input files are in order according to normalized
    accession numbers.

    Note that this script has been tested against a "normal" Modes XML Object
    file. It is explicitly not guaranteed to work with arbitrary XML files.
    For example, multiple attributes are allowed on elements and they can be
    in any order. This script may issue false "changed" output in those cases.
"""
import argparse
import os.path
import sys
from colorama import Fore, Style
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfgutil import Config, DEFAULT_MDA_CODE
from utl.normalize import normalize_id, sphinxify
from utl.normalize import if_not_sphinx


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def nextobj(pnum: int, iterparser):
    objectlevel = 0
    while True:
        try:
            event, obj = next(iterparser)
        except StopIteration:
            trace(2, 'End of file {}', pnum)
            return None, None, None
        if event == 'start':
            if obj.tag == record_tag:
                objectlevel += 1
            continue
        # It's an "end" event.
        if obj.tag != record_tag:
            continue
        objectlevel -= 1
        if objectlevel:
            continue  # It's not a top level Object.
        idelem = obj.find(record_id_xpath)
        idnum = idelem.text if idelem is not None else None
        nidnum = normalize_id(idnum)
        objstr = ET.tostring(obj)
        trace(2, 'File {} {}', pnum, nidnum)
        if nidnum <= oldid[pnum]:
            trace(0, "Objects out of order in file {}. Old ID = {}, "
                     "New ID = {}", pnum, oldid[pnum], nidnum,
                  color=Fore.RED)
            sys.exit(-1)
        objcount[pnum] += 1
        oldid[pnum] = nidnum
        return obj, nidnum, objstr


def main():
    global objcount, deleted, added, replaced, written, skipped
    ip1 = ET.iterparse(infile1, events=('start', 'end'))
    ip2 = ET.iterparse(infile2, events=('start', 'end'))
    obj1, nid1, objstr1 = nextobj(1, ip1)
    obj2, nid2, objstr2 = nextobj(2, ip2)
    #
    #   Write output head
    #
    declaration = f'<?xml version="1.0" encoding="{_args.encoding}"?>\n'
    outfile.write(bytes(declaration, encoding=_args.encoding))
    outfile.write(b'<Interchange>\n')
    #
    #   Main Loop
    #
    while True:
        if nid2 is None:
            # Any objects left in infile2 are deleted
            if obj1 is None:
                break
            obj1.clear()
            trace(2, "Deleting object at end: {}", nid1)
            obj1, nid1, objstr1 = nextobj(1, ip1)
            deleted += 1
            continue
        if nid1 is None:
            # The objects in infile2 are new. Write them all
            written += 1
            added += 1
            trace(2, "Write new element at end {}", nid2)
            outfile.write(objstr2)
            obj2.clear()
            obj2, nid2, objstr2 = nextobj(2, ip2)
            continue
        if nid1 == nid2:
            if objstr1 != objstr2:
                trace(2, "Write changed element {}", nid2)
                written += 1
                replaced += 1
                outfile.write(objstr2)
            else:
                skipped += 1
                trace(2, "Skip unchanged {}", nid1)
            obj1.clear()
            obj1, nid1, objstr1 = nextobj(1, ip1)
            obj2.clear()
            obj2, nid2, objstr2 = nextobj(2, ip2)
            continue
        if nid1 < nid2:
            # The old object has been deleted
            trace(2, "Deleting object: {}", nid1)
            deleted += 1
            obj1.clear()
            obj1, nid1, objstr1 = nextobj(1, ip1)
            continue
        # nid2 < nid1
        # A new object has been inserted.
        trace(2, "Write new element {}", nid2)
        added += 1
        written += 1
        outfile.write(objstr2)
        obj2.clear()
        obj2, nid2, objstr2 = nextobj(2, ip2)

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
    parser.add_argument('outfile', help='''
        The XML file containing the changed or added Object elements.''')
    parser.add_argument('-e', '--encoding', default='utf-8', help='''
        Set the output encoding. The default is "utf-8".
        ''')
    parser.add_argument('--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code, used in normalizing the accession number.''' +
                        if_not_sphinx(''' The default is "{DEFAULT_MDA_CODE}".
                        ''', calledfromsphinx))
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


def s(i: int):
    return '' if i == 1 else 's'


calledfromsphinx = True
if __name__ == '__main__':
    assert sys.version_info >= (3, 11)
    calledfromsphinx = False
    #
    # Global variables
    #
    objcount = [None, 0, 0]
    deleted = added = replaced = written = skipped = 0
    oldid = [None, '', '']
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    basename = os.path.basename(sys.argv[0])
    trace(1, 'Begin {}', basename.split(".")[0], color=Fore.GREEN)
    infile1 = open(_args.infile1)
    infile2 = open(_args.infile2)
    outfile = open(_args.outfile, 'wb')
    config = Config(mdacode=_args.mdacode, dump=_args.verbose >= 2)
    record_tag = config.record_tag
    record_id_xpath = config.record_id_xpath
    main()
    trace(1, '{} objects in old file.', objcount[1])
    trace(1, '{} objects in new file.', objcount[2])
    trace(1, '{} object{} deleted.', deleted, s(deleted))
    trace(1, '{} object{} added.', added, s(added))
    trace(1, '{} object{} replaced.', replaced, s(replaced))
    trace(1, '{} object{} written to diff file.', written, s(written))
    trace(1, 'End {}', basename.split(".")[0], color=Fore.GREEN)
