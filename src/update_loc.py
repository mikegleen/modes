# -*- coding: utf-8 -*-
"""
Set the normal location and current location to new locations from a CSV file.
"""
import argparse
import csv
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def loadlocs():
    location = {}
    with open(_args.csvfile, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            location[row[0].strip()] = row[1].strip()
    return location


def main():
    locs = loadlocs()
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find('./ObjectIdentity/Number')
        idnum = idelem.text if idelem else None
        if _args.verbose > 1:
            print(idnum)
        if idnum in locs:
            objlocs = elem.findall('./ObjectLocation/Location')
            for ol in objlocs:
                ol.text = locs[idnum]
        outfile.write(ET.tostring(elem, encoding='us-ascii'))
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Set the normal location and current location to the new location from
        a CSV file containing rows of the format: <object number>,<location>.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-c', '--csvfile', required=True, help='''
        The CSV file mapping the object number to its location''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
