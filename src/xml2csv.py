# -*- coding: utf-8 -*-
"""

"""
import argparse
import codecs
import csv
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


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


def read_dsl(dslf):
    cols = []
    for line in dslf:
        line = line.strip()
        if not line or line[0] == '#':
            continue
        row = line.split(None, 1)
        if len(row) > 1:
            row[1] = row[1].strip('\'"')  # remove leading & trailing quotes
        if row[0].lower() == 'column':
            cols.append(row[1])
    return cols


def main(inf, outf, dslf):
    outcsv = opencsvwriter(outf)
    cols = read_dsl(dslf)
    for event, elem in ET.iterparse(infile):
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
        Set the normal location and/or current location to the new location
        from a CSV file with rows of the format: <object number>,<location>.
        If the location in the CSV file differs from the location in the XML
        file, update the Date/DateBegin element to today's date.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output CSV file.''')
    parser.add_argument('-b', '--bom', action='store_true', help='''
        Insert a BOM at the front of the output CSV file.''')
    parser.add_argument('-f', '--dslfile', required=True, help='''
        The DSL describing the columns to extract''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object.''')
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
