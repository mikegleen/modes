# -*- coding: utf-8 -*-
"""
    Create a report showing the percent completion of priority fields.
"""
import argparse
import codecs
import collections
import csv
import json
import math
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

import utl.cfgutil as cfgutil

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
    global nrows, tally, nobjects, titles
    outcsv = opencsvwriter(outf)
    config = cfgutil.read_yaml_cfg(dslf)
    cfg = config.columns
    if not cfgutil.validate_yaml_cfg(cfg):
        sys.exit(1)
    # Exclude "ifattrib" as it doesn't create a column
    titles = [stmt['title'] for stmt in cfg if 'title' in stmt]
    titles = ['ID'] + titles
    trace(1, 'columns: {}', ', '.join([str(x) for x in titles]))
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
            attrib = stmt.get('attribute')
            e = elem.find(elt)
            if cmd == 'attrib':
                text = e.get(attrib)
            elif cmd == 'ifattrib':
                value = stmt['value']
                eltattrib = e.get(attrib)
                if eltattrib == value:
                    continue  # ifattrib doesn't create a column
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
            nrows += 1
            outcsv.writerow(data)
        if _args.short:
            break


def getargs():
    parser = argparse.ArgumentParser(description='''
    Extract fields from an XML file, creating a CSV file with the specified
    fields. The first column is hard-coded as './ObjectIdentity/Number'.
    Subsequent column_paths are defined in a YAML file containing the following:
    
    ---
    cmd: column | attrib | ifattrib | required | count
    elt: <xpath statement selected an element>
    title: '<text in quotes if containing white space>'
    value: '<text to match an attribute for ifattrib command>'
    attribute: '<attribute name to fetch if cmd is "attrib">'
    
    if the title statement is omitted, the final element in elt is used.
    ''', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile',  help='''
        The output CSV file.''')
    parser.add_argument('-f', '--fields', action='store_true', help='''
        Write a row at the front of the CSV file containing the field names.'''
                        )
    parser.add_argument('-b', '--bom', action='store_true', help='''
        Insert a BOM at the front of the output CSV file.''')
    parser.add_argument('-c', '--cfgfile', help='''
        The YAML file describing the column paths to extract''')
    parser.add_argument('-j', '--jsonfile', help='''
        The JSON file to write the results to''')
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
    nrows = 0
    nobjects = 0
    tally = collections.defaultdict(int)
    titles = []
    infile = open(_args.infile)
    cfgfile = open(_args.cfgfile) if _args.cfgfile else None
    main(infile, _args.outfile, cfgfile)
    trace(1, f'{nobjects} objects read.')
    trace(1, f'{nrows} rows written to {_args.outfile}.')
    tallylist = []
    for ix, title in enumerate(titles):
        percent = math.floor(float(tally[ix]) * 100. / float(nrows))
        print(f'{str(title):25} {tally[ix]:3}/{nrows} ({percent}%)')
        tallylist.append((title, tally[ix]))
    if _args.jsonfile:
        tree = {'nobjects': nobjects, 'nrows': nrows, 'tallylist': tallylist}
        with open(_args.jsonfile, 'w') as jsonfile:
            json.dump(tree, jsonfile, ensure_ascii=True, indent=4)
