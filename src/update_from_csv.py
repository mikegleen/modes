# -*- coding: utf-8 -*-
"""
    Read a CSV file containing two columns. The first column is the index and
    the second column is the field defined by the XPATH statement in the DSL
    file as defined in xml2csv.py. Update the XML file with data from the
    CSV file.
"""
import argparse
import codecs
import csv
from datetime import date
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


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


def loadnewvals():
    """
    Read the CSV file containing objectid -> new element value
    :return: the dictionary containing the mappings
    """
    newval_dict = {}
    with codecs.open(_args.mapfile, 'r', 'utf-8-sig') as mapfile:
        reader = csv.reader(mapfile)
        for row in reader:
            newval_dict[row[0].strip()] = row[1].strip()
    return newval_dict


def one_element(elem, idnum):
    """
    If the location in the newlocs dictionary is different from the location
    in the XML, update the XML.
    Note that we have already tested that idnum is in newvals.

    :param elem: the Object
    :param idnum: the ObjectIdentity/Number text
    :return: None
    """
    target = elem.find(columns[0])
    if target is None:
        trace(1,"Cannot find target '{}' for {}", columns[0], idnum)
        return
    newtext = newvals[idnum]  # we've already checked that it's there
    text = target.text
    if text != newtext:
        trace(2, 'Updated {}: "{}" -> "{}"', idnum, text, newtext)
        target.text = newtext
    else:
        trace(2, 'Unchanged {}: {}', idnum, text)


def main():
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find('./ObjectIdentity/Number')
        idnum = idelem.text if idelem is not None else None
        trace(3, 'idnum: {}', idnum)
        if idnum and idnum in newvals:
            one_element(elem, idnum)
            del newvals[idnum]
        else:
            trace(1, 'Not in CSV file: {}', idnum)
        outfile.write(ET.tostring(elem, encoding='us-ascii'))
    outfile.write(b'</Interchange>')
    for idnum in newvals:
        trace(1, 'In CSV but not XML: {}', idnum)


def getargs():
    parser = argparse.ArgumentParser(description='''
        Read a CSV file containing two columns. The first column is the index and
        the second column is the field defined by the XPATH statement in the DSL
        file as defined in xml2csv.py. Update the XML file with data from the
        CSV file.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-e', '--empty', action='store_true', help='''
        Print a warning if the target element is not empty.''')
    parser.add_argument('-f', '--dslfile', required=True,
                        type=argparse.FileType('r'), help='''
        The DSL describing the columns to extract''')
    parser.add_argument('-m', '--mapfile', required=True, help='''
        The CSV file mapping the object number to the new element value.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    today = date.today().isoformat()
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    newvals = loadnewvals()
    columns = read_dsl(_args.dslfile)
    main()
