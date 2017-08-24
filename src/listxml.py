# -*- coding: utf-8 -*-
"""
    Examine an XML file and report tags containing text, showing their full
    paths.
"""
import argparse
from collections import defaultdict
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def one_elt(elt, path):
    path += '/' + elt.tag
    if elt.text is not None:
        tagcount[path] += 1
    if not elt:
        return
    for e in elt:
        one_elt(e, path)


def main():
    for event, obj in ET.iterparse(infile):
        if obj.tag != 'Object':
            continue
        for elt in obj:
            one_elt(elt, '.')
    for tag, count in sorted(tagcount.items()):
        print(tag, count)


def getargs():
    parser = argparse.ArgumentParser(description='''
        Scan an XML file and report which tags have text.
        ''')
    parser.add_argument('infile', help='''
        The XML file to scan.''')
    # parser.add_argument('outfile', help='''
    #     The output report file.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    tagcount = defaultdict(int)
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    _args = getargs()
    infile = open(_args.infile)
    main()
