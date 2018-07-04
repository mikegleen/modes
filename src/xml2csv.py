# -*- coding: utf-8 -*-
"""
    Extract fields from an XML file, creating a CSV file with the specified
    fields.

    The first column is hard-coded as './ObjectIdentity/Number'. Subsequent
    column_paths are defined in a config file containing "column" statements
    each with one parameter, the XPATH of the column to extract.
"""
import argparse
import codecs
import csv
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from cfg.cfgutil import read_cfg


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def opencsvwriter(filename):
    # csvfile = open(filename, 'w', newline='')
    encoding = 'utf-8-sig' if _args.bom else 'utf-8'
    csvfile = codecs.open(filename, 'w', encoding)  # insert BOM at front
    outcsv = csv.writer(csvfile, delimiter=',')
    # outcsv.writerow(HEADING)
    trace(1, 'Output: {}', filename)
    return outcsv


def main(inf, outf, dslf):
    outcsv = opencsvwriter(outf)
    cols = read_cfg(dslf)
    for event, elem in ET.iterparse(inf):
        if elem.tag != 'Object':
            continue
        data = []
        for col in cols:
            elt = elem.find(col)
            if elt is not None:
                data.append(elt.text)
        outcsv.writerow(data)
        if _args.short:
            break


def getargs():
    parser = argparse.ArgumentParser(description='''
    Extract fields from an XML file, creating a CSV file with the specified
    fields. The first column is hard-coded as './ObjectIdentity/Number'.
    Subsequent column_paths are defined in a DSL file containing "column" statements
    each with one parameter, the XPATH of the column to extract.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output CSV file.''')
    parser.add_argument('-b', '--bom', action='store_true', help='''
        Insert a BOM at the front of the output CSV file.''')
    parser.add_argument('-f', '--dslfile', required=True, help='''
        The DSL describing the column_paths to extract''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    _args = getargs()
    infile = open(_args.infile)
    dslfile = open(_args.dslfile)
    main(infile, _args.outfile, dslfile)
