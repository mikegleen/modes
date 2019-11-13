# -*- coding: utf-8 -*-
"""
    Create a report showing the percent completion of priority fields.
"""
import argparse
import codecs
import collections
import csv
import math
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import read_yaml_cfg


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def opencsvwriter(filename):
    encoding = 'utf-8-sig' if _args.bom else 'utf-8'
    csvfile = codecs.open(filename, 'w', encoding)
    outcsv = csv.writer(csvfile, delimiter=',')
    trace(1, 'Output: {}', filename)
    return outcsv


def main(inf, outf, dslf):
    global nlines, tally, nobjects, titles
    outcsv = opencsvwriter(outf)
    cfg = read_yaml_cfg(dslf)
    titles = [stmt['title'] for stmt in cfg if stmt['title'] is not None]
    titles = ['ID'] + titles
    trace(1, 'columns: {}', ', '.join(titles))
    if _args.fields:
        outcsv.writerow(titles)
    for event, elem in ET.iterparse(inf):
        if elem.tag != 'Object':
            continue
        writerow = True
        nobjects += 1
        # data[0] = Id
        data = [elem.find('./ObjectIdentity/Number').text]
        for stmt in cfg:
            cmd = stmt['cmd']
            elt = stmt['elt']
            attrib = stmt['attribute'] if 'attribute' in stmt else None
            e = elem.find(elt)
            if cmd == 'attrib':
                text = e.get(attrib)
            elif cmd == 'ifattrib':
                value = stmt['value']
                eltattrib = e.get(attrib)
                if eltattrib == value:
                    continue
                else:
                    writerow = False
                    break
            elif cmd == 'count':
                count = len(list(elem.findall(elt)))
                text = f'{count}'
            elif cmd == 'required':
                text = e.text.strip()
                if not text:
                    writerow = False
                    break
            elif e is None or e.text is None:
                text = ''
            else:
                text = e.text.strip()
            if _args.maxwidth:
                text = text[:_args.maxwidth]
            data.append(text)
        if writerow:
            # For each column count the rows where that column is populated.
            for i, dat in enumerate(data):
                tally[i] += 1 if data[i] else 0
            nlines += 1
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
    parser.add_argument('outfile',  help='''
        The output CSV file.''')
    parser.add_argument('-f', '--fields', action='store_true', help='''
        Write a row at the front of the CSV file containing the field names.'''
                        )
    parser.add_argument('-b', '--bom', action='store_true', help='''
        Insert a BOM at the front of the output CSV file.''')
    parser.add_argument('-c', '--cfgfile', required=False, help='''
        The config file describing the column_paths to extract''')
    parser.add_argument('-m', '--maxwidth', type=int, help='''
        The maximum column width in the output CSV file. The default is unlimited.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    nlines = 0
    nobjects = 0
    tally = collections.defaultdict(int)
    titles = []
    infile = open(_args.infile)
    cfgfile = open(_args.cfgfile) if _args.cfgfile else None
    main(infile, _args.outfile, cfgfile)
    trace(1, f'{nobjects} lines read.')
    trace(1, f'{nlines} lines written to {_args.outfile}.')
    for ix, title in enumerate(titles):
        percent = math.floor(float(tally[ix]) * 100. / float(nlines))
        print(f'{title:25} {tally[ix]:3}/{nlines} ({percent}%)')
