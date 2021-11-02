# -*- coding: utf-8 -*-
"""
    This script expects two entries in the config. It will display the count
    of times the two entries were identical and when they were "alike",
    meaning that the contents of one was in the other.

    The original purpose of this program was to compare the Title and
    BriefDescription elements which were largely redundant. See
    title_and_briefdes.yml.
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


def one_object(parent, doc1, doc2, idnum) -> tuple:
    """
    :param parent: the Object from the old file
    :param doc1:
    :param doc2:
    :param idnum:
    :return: 5-tuple with 1 if true, otherwise zero:
    (match, text1 in text2, text2 in text 1, text1 empty, text2 empty)
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
    if not text1:
        trace(3, '    {}', 'text1 empty')
        return 0, 0, 0, 1, 0
    elif not text2:
        trace(3, '    {}', 'text2 empty')
        return 0, 0, 0, 0, 1
    elif text1 == text2:
        trace(3, '    {}', 'identical')
        return 1, 0, 0, 0, 0
    elif text1 in text2:
        trace(3, '    {}', 'like')
        return 0, 1, 0, 0, 0
    elif text2 in text1:
        trace(3, '    {}', 'revlike')
        return 0, 0, 1, 0, 0
    else:
        trace(3, '    {}', 'nomatch')
        return 0, 0, 0, 0, 0


def main():
    doc_a = config.col_docs[0]
    doc_b = config.col_docs[1]
    objectlevel = 0
    nhits = nlikes = nrevlikes = nnomatch = 0
    nnot1 = nnot2 = 0
    ntotal = 0
    results = ['Match', f'{doc_a[Stmt.TITLE]} in {doc_b[Stmt.TITLE]}',
               f'{doc_b[Stmt.TITLE]} in {doc_a[Stmt.TITLE]}']
    for event, oldobject in ET.iterparse(_args.infile,
                                         events=('start', 'end')):
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
        response = one_object(oldobject, doc_a, doc_b, idnum)
        ntotal += 1
        hits, likes, revlikes, not1, not2 = response
        nhits += hits
        nlikes += likes
        nrevlikes += revlikes
        nnot1 += not1
        nnot2 += not2
        ismatch = hits + likes + revlikes  # 0 or 1
        nnomatch += 1 - ismatch
        if _args.output and ismatch:
            print(f'{idnum},' + ''.join(
                [results[i] for i, x in enumerate(response[:3]) if x]),
                  file=_args.output)
        oldobject.clear()
    print(f'identical: {nhits}')
    print(f'{doc_a[Stmt.TITLE]} in {doc_b[Stmt.TITLE]}: {nlikes}')
    print(f'{doc_b[Stmt.TITLE]} in {doc_a[Stmt.TITLE]}: {nrevlikes}')
    print(f'nomatch: {nnomatch}')
    print(f'{doc_a[Stmt.TITLE]} empty: {nnot1}')
    print(f'{doc_b[Stmt.TITLE]} empty: {nnot2}')
    print(f'{ntotal=}')


def getparser():
    parser = argparse.ArgumentParser(description='''
    This script expects two entries in the config. It will display the count
    of times the two entries were identical and when they were "alike",
    meaning that the contents of one was in the other.
    
    This is a somewhat specialized use case where the Title and BriefDescription
    fields duplicate each other.
        ''')
    parser.add_argument('infile', type=argparse.FileType('r'), help='''
        The input XML file''')
    parser.add_argument('-c', '--cfgfile', required=True, help='''
        The config file describing the Object elements to compare
        ''')
    parser.add_argument('-i', '--caseinsensitive', action='store_true', help='''
        Convert all values to lower case before comparison.''')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        dest='output', help='''
        If specified, the CSV file with per-object values.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


called_from_sphinx = True


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    called_from_sphinx = False
    _args = getargs(sys.argv)
    cfgfile = open(_args.cfgfile)
    config = Config(cfgfile, dump=_args.verbose >= 2)
    main()
    basename = os.path.basename(sys.argv[0])
    trace(1, f'End {basename.split(".")[0]}')
