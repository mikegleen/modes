# -*- coding: utf-8 -*-
"""
    For each config entry, report the count of different text values.

"""
import argparse
from collections import defaultdict
import os.path
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfgutil import Config, Stmt


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_object(parent, document, tally, lastid, idnum):
    """
    :param parent: the Object from the old file
    :param document: The YAML document with config info
    :param tally: the dict containing the accumulated count
    :param lastid: dict containing the last object id that updated this entry
    :param idnum:
    :return: None.
    """
    global nofinds
    eltstr = document[Stmt.XPATH]
    element = parent.find(eltstr)
    if element is None:
        trace(3, 'Nofind: {} {}', idnum, eltstr)
    elif element.text:
        text = element.text.strip()
        if _args.caseinsensitive:
            text = text.lower()
        tally[text] += 1
        lastid[text] = idnum


def main():
    global nofinds
    for doc in config.col_docs:
        nofinds = 0
        objectlevel = 0
        tally = defaultdict(int)
        lastid = {}
        infile = open(_args.infile)
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
            idelem = oldobject.find(config.record_id_xpath)
            idnum = idelem.text if idelem is not None else ''
            trace(3, 'idnum: {}', idnum)
            one_object(oldobject, doc, tally, lastid, idnum)
            oldobject.clear()
        print(f"\n{doc[Stmt.XPATH]} ({len(tally)}"
              f" unique value{'s' if len(tally) > 1 else ''})")
        print(f'{"-" * len(doc[Stmt.XPATH])}')
        for word, count in sorted(tally.items()):
            # s = word.encode()
            # print(f'{count:4},"{word}","{[hex(i) for i in s]}"')
            print(f'{count:4},"{word}"{", " + lastid[word] if count == 1 else ""}')
        if nofinds:
            print(f'Nofinds: {nofinds}')
        infile.close()


def getargs():
    parser = argparse.ArgumentParser(description='''
    For each config entry, report the count of different text values.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('-c', '--cfgfile', required=True, help='''
        The config file describing the Object elements to include in the
        output''')
    parser.add_argument('-i', '--caseinsensitive', action='store_true', help='''
        Convert all keywords to lower case.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    nofinds = 0
    _args = getargs()
    cfgfile = open(_args.cfgfile)
    config = Config(cfgfile, title=True, dump=_args.verbose >= 2)
    main()
    basename = os.path.basename(sys.argv[0])
    print(f'End {basename.split(".")[0]}')
