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

from utl.cfgutil import read_cfg, fieldnames


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
    cfg = read_cfg(dslf)
    cols = cfg.columns
    reqd = cfg.required
    trace(1, 'columns: {}', ', '.join(cols))
    trace(1, 'required: {}', ', '.join(reqd))
    if _args.fields:
        data = fieldnames(cols)
        outcsv.writerow(data)
    for event, elem in ET.iterparse(inf):
        if elem.tag != 'Object':
            continue
        writerow = True
        # data[0] = Id
        data = [elem.find('./ObjectIdentity/Number').text]
        for col in cols:
            elt = elem.find(col)
            if elt is None or elt.text is None:
                text = ''
            else:
                text = elt.text.strip()
            if not text and col in reqd:
                writerow = False
                break
            data.append(text)
        if writerow:
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
    parser.add_argument('-f', '--fields', action='store_true', help='''
        Write a row at the front of the CSV file containing the field names.'''
                        )
    parser.add_argument('-b', '--bom', action='store_true', help='''
        Insert a BOM at the front of the output CSV file.''')
    parser.add_argument('-c', '--cfgfile', required=True, help='''
        The config file describing the column_paths to extract''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
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
    cfgfile = open(_args.cfgfile)
    main(infile, _args.outfile, cfgfile)
