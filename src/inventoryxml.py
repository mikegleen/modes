# -*- coding: utf-8 -*-
"""
    Examine an XML file and report which tags contain text.
"""
import argparse
from collections import defaultdict
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def one_object(elt):
    typecount[elt.attrib['elementtype']] +=1
    for e in elt.iter():
        if e.tag == 'Description':
            try:
                description_type_count[e.attrib['elementtype']] += 1
            except KeyError:
                pass

        if e.text is not None:
            tagcount[e.tag] += 1


def main():
    for event, obj in ET.iterparse(infile):
        if obj.tag != 'Object':
            continue
        one_object(obj)
    for tag, count in sorted(tagcount.items()):
        print(tag, count)
    print('\n---elementtypes:')
    for typ, count in sorted(typecount.items()):
        print(typ, count)
    print('\n---description_type_count:')
    for typ, count in sorted(description_type_count.items()):
        print(typ, count)


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
    assert sys.version_info >= (3, 6)
    description_type_count = defaultdict(int)
    tagcount = defaultdict(int)
    typecount = defaultdict(int)
    _args = getargs()
    infile = open(_args.infile)
    main()
