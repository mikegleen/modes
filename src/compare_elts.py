# -*- coding: utf-8 -*-
"""
    This script expects two entries in the config. It will display the count
    of times the two entries were identical and when they were "alike",
    meaning that the contents of one was in the other.
"""
import argparse
import os.path
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfgutil import Config, Stmt


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_object(parent, doc1, doc2, idnum):
    """
    :param parent: the Object from the old file
    :param doc1: 
    :param doc2:
    :param idnum:
    :return: tuple (1,0) = exact match, (0,1) = similar
    """
    def get_text(doc):
        eltstr = doc[Stmt.XPATH]
        elt = parent.find(eltstr)
        text = ''
        if elt is None:
            trace(3, 'Nofind: {} {}', idnum, elt)
        elif elt.text:
            text = elt.text.strip()
            if _args.caseinsensitive:
                text = text.lower()
        return text

    text1 = get_text(doc1)
    text2 = get_text(doc2)
    trace(3, '    {}', text1)
    trace(3, '    {}', text2)
    if text1 == text2:
        trace(3, '    {}', 'hit')
        return 1, 0, 0
    elif text1 in text2:
        trace(3, '    {}', 'like')
        return 0, 1, 0
    elif text2 in text1:
        trace(3, '    {}', 'revlike')
        return 0, 0, 1
    else:
        trace(3, '    {}', 'nomatch')
        return 0, 0, 0


def main():
    doc_a = config.col_docs[0]
    doc_b = config.col_docs[1]
    infile = open(_args.infile)
    objectlevel = 0
    nhits = nlikes = nrevlikes = nnomatch = 0
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
        hits, likes, revlikes = one_object(oldobject, doc_a, doc_b, idnum)
        nhits += hits
        nlikes += likes
        nrevlikes += revlikes
        nnomatch += 1 - (hits + likes + revlikes)
        oldobject.clear()
    print(f'{nhits=} {nlikes=} {nrevlikes=} {nnomatch=}')


def getargs():
    parser = argparse.ArgumentParser(description='''
    For the first two documents in the config file, compare the elements and
    report how many are identical and how many are similar.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('-c', '--cfgfile', required=True, help='''
        The config file describing the Object elements to compare
        ''')
    parser.add_argument('-i', '--caseinsensitive', action='store_true', help='''
        Convert all values to lower case.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    _args = getargs()
    cfgfile = open(_args.cfgfile)
    config = Config(cfgfile, title=True, dump=_args.verbose >= 2)
    main()
    basename = os.path.basename(sys.argv[0])
    trace(1, f'End {basename.split(".")[0]}')
