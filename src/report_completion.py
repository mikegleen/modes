# -*- coding: utf-8 -*-
"""
    Create a report showing the percent populated of specified fields.
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


def main(inf, dslf):
    """

    :param inf: The input XML file containing our objects
    :param dslf: The Data Specific Language YAML file containing the config.
    :return: A report is produced showing how complete object fields are.
    """
    nobjects = 0
    nrows = 0
    tally = collections.defaultdict(int)
    config = cfgutil.Config(dslf, title=True,
                            dump=True if _args.verbose > 1 else False)
    col_docs = config.col_docs
    titles = [stmt['title'] for stmt in col_docs]
    if not config.skip_number:
        titles = ['ID'] + titles
    trace(1, 'columns: {}', ', '.join([str(x) for x in titles]))
    for event, elem in ET.iterparse(inf):
        if elem.tag != 'Object':
            continue
        writerow = cfgutil.select(elem)
        nobjects += 1
        # data[0] = Id unless skip_number is set in the config
        data = []
        if not config.skip_number:
            data = [elem.find(config.record_tag.text)]
        for stmt in col_docs:
            cmd = stmt['cmd']
            elt = stmt['elt']
            attribute = stmt.get('attribute')
            e: ET.Element = elem.find(elt)
            if cmd == 'attrib':
                text = e.get(attribute)
            elif cmd == 'count':
                count = len(list(elem.findall(elt)))
                text = f'{count}'
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
        if _args.short:
            break
    trace(1, f'{nobjects} objects read.')
    trace(1, f'{nrows} objects selected.')
    tallylist = []
    for ix, title in enumerate(titles):
        percent = math.floor(float(tally[ix]) * 100. / float(nrows))
        print(f'{str(title):25} {tally[ix]:3}/{nrows} ({percent}%)')
        tallylist.append((title, tally[ix]))
    if _args.jsonfile:
        tree = {'nobjects': nobjects, 'nrows': nrows, 'tallylist': tallylist}
        with open(_args.jsonfile, 'w') as jsonfile:
            json.dump(tree, jsonfile, ensure_ascii=True, indent=4)


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
    infile = open(_args.infile)
    cfgfile = open(_args.cfgfile) if _args.cfgfile else None
    main(infile, cfgfile)
