# -*- coding: utf-8 -*-
"""
    List the elementtype attributes of the Object elements.
"""
import argparse
from collections import defaultdict
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def main(inf):
    attribs = defaultdict(int)
    for event, elem in ET.iterparse(inf):
        if elem.tag != 'Object':
            continue
        elementtype = elem.get('elementtype', default='notype')
        attribs[elementtype] += 1
        if _args.type and elementtype == _args.type:
            num = elem.find('./ObjectIdentity/Number')
            title = elem.find('./Identification/Title')
            print(num.text, title.text[:50])
    if _args.type:
        return
    for e, c in attribs.items():
        print(e, c)


def getargs():
    parser = argparse.ArgumentParser(description='''
    List the elementtype attributes of the Object elements.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('-t', '--type', help='''
        Print the object number of all of the Object elements of this type.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    _args = getargs()
    infile = open(_args.infile)
    main(infile)
