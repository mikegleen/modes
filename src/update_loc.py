# -*- coding: utf-8 -*-
"""
Set the normal location and current location to new locations from a CSV file.
"""
import argparse
import csv
from datetime import date
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def loadlocs():
    """
    Read the CSV file containing objectid -> location mappings
    :return: the dictionary containing the mappings
    """
    location_dict = {}
    with open(_args.csvfile, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            location_dict[row[0].strip()] = row[1].strip()
    return location_dict


def one_objectlocation(ol, idnum):
    """
    If the location in the newlocs dictionary is different from the location
    in the XML, update the XML and insert today's date.

    :param ol: the ObjectLocation element
    :param idnum: the ObjectIdentity/Number text
    :return:
    """
    location = ol.find('./Location')
    if location.text is not None:
        text = location.text.strip().upper()
    else:
        text = None
    newtext = newlocs[idnum]  # we've already checked that it's there
    if text != newtext:
        trace(2, 'Updated: {} -> {}', text, newtext)
        location.text = newtext
        datebegin = ol.find('./Date/DateBegin')
        datebegin.text = today
    else:
        trace(2, 'Unchanged: {}', text)


def main():
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find('./ObjectIdentity/Number')
        idnum = idelem.text if idelem is not None else None
        trace(2, '{}', idnum)
        if idnum in newlocs:
            objlocs = elem.findall('./ObjectLocation')
            for ol in objlocs:
                one_objectlocation(ol, idnum)
        else:
            trace(1, 'Not in CSV file: {}', idnum)
        outfile.write(ET.tostring(elem, encoding='us-ascii'))
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Set the normal location and current location to the new location from
        a CSV file containing rows of the format: <object number>,<location>.
        If the location in the CSV file differs from the location in the XML
        file, update the Date/DateBegin element to today's date.
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
    newlocs = loadlocs()
    today = date.today().isoformat()
    main()
