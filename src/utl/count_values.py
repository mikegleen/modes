# -*- coding: utf-8 -*-
"""
    For a single field, display the number of occurances of each value.
"""
import argparse
from collections import defaultdict
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import Config
from utl.zipmagic import openfile
from utl.normalize import sphinxify


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def main(inf):
    values = defaultdict(int)
    xpath = get_xpath()
    trace(2, 'xpath: {}', xpath)
    nonepathcount = 0
    for event, elem in ET.iterparse(inf):
        if elem.tag != 'Object':
            continue
        path = elem.find(xpath)
        if path is None:
            nonepathcount += 1
        else:
            value = path.text
            if value is None:
                value = 'None'
            values[value] += 1
            if _args.type and value in _args.type:
                num = elem.find('./ObjectIdentity/Number')
                print(num.text, value[:_args.width])
    if not _args.type:
        # for e, c in values.items():
        # for e, c in [(e, c) for e, c in values.items()]:
        for e, c in sorted(values.items()):
            print(e, c)
        print(f'{len(values)} unique values.')
    return nonepathcount


def get_xpath():
    if _args.xpath:
        return _args.xpath
    else:
        config: Config = Config(_args.cfgfile, dump=_args.verbose > 1,
                                allow_required=True)
        if len(config.col_docs) > 1:
            raise ValueError('Only a single column command is allowed in the'
                             'config file.')
        return config.col_docs[0].xpath


def getargs():
    parser = argparse.ArgumentParser(description='''
    For a single field, display the number of occurances of each value.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('-c', '--cfgfile',
                        type=argparse.FileType('r'), help=sphinxify('''
        The YAML file describing the column path containing values to count.
        The config file may contain only a single ``column`` command. Specify 
        this or the --xpath parameter.
    ''', calledfromsphinx))
    parser.add_argument('-t', '--type', action='append', help=sphinxify('''
        Print the object number of all of the Object elements of this type.
        Multiple --type arguments may be entered.''', calledfromsphinx))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-w', '--width', type=int, default=50, help='''
        Set the width of the field printed. The default is 50.
        ''')
    parser.add_argument('-x', '--xpath', help=sphinxify('''
        Specify the xpath of the field containing values to count. Specify this
        or the --cfgfile parameter.
        ''', calledfromsphinx))
    args = parser.parse_args()
    if bool(args.cfgfile) == bool(args.xpath):
        raise ValueError('Exactly one of the --cfgfile and --xpath parameters'
                         ' must be specified.')
    return args


calledfromsphinx = True
if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    calledfromsphinx = False
    _args = getargs()
    infile = openfile(_args.infile)
    npc = main(infile)
    if npc:
        print(f'Number of objects not containing the xpath: {npc}')
