# -*- coding: utf-8 -*-
"""
    List the elementtype attributes of the Object elements.
"""
import argparse
from collections import defaultdict
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.zipmagic import openfile


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
            print(num.text, title.text[:_args.width])
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
    parser.add_argument('-w', '--width', type=int, default=50, help='''
        Set the width of the title printed. The default is 50.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    infile = openfile(_args.infile)
    main(infile)
