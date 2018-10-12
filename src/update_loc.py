# -*- coding: utf-8 -*-
"""
Set the normal location and/or the current location to new locations
from a CSV file.
"""
import argparse
import codecs
import csv
from datetime import date
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl import normalize_date as nd


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def loadlocs():
    """
    Read the CSV file containing objectid -> location mappings
    :return: the dictionary containing the mappings
    """
    location_dict = {}
    with codecs.open(_args.mapfile, 'r', 'utf-8-sig') as mapfile:
        reader = csv.reader(mapfile)
        for row in reader:
            location_dict[row[0].strip()] = row[1].strip()
    return location_dict


def one_objectlocation(ol, idnum):
    """
    If the location in the newlocs dictionary is different from the location
    in the XML, update the XML, insert the date specified on the command line,
    and delete the idnum from the global "newlocs" dictionary.
    Note that we have already tested that idnum is in newlocs.

    :param ol: the ObjectLocation element
    :param idnum: the ObjectIdentity/Number text
    :return: True if the object is updated, False otherwise
    """
    updated = False
    location = ol.find('./Location')
    if location.text is not None:
        text = location.text.strip().upper()
    else:
        text = None
    newtext = newlocs[idnum]  # we've already checked that it's there
    if text != newtext:
        trace(2, 'Updated {}: {} -> {}', idnum, text, newtext)
        location.text = newtext
        datebegin = ol.find('./Date/DateBegin')
        if datebegin is not None:  # normal location doesn't have a date
            datebegin.text = _args.date
        updated = True
    else:
        trace(2, 'Unchanged: {}', text)
    return updated


def main():
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    for event, elem in ET.iterparse(infile):
        updated = False
        if elem.tag != 'Object':
            continue
        idelem = elem.find('./ObjectIdentity/Number')
        idnum = idelem.text if idelem is not None else None
        trace(2, 'idnum: {}', idnum)
        if idnum in newlocs:
            objlocs = elem.findall('./ObjectLocation')
            for ol in objlocs:
                loc = ol.get('elementtype')
                if (_args.normal and loc == 'normal location') or (
                    _args.current and loc == 'current location'
                ):
                    updated = one_objectlocation(ol, idnum)
            del newlocs[idnum]
        else:
            if not _args.update:
                trace(1, 'Not in CSV file: {}', idnum)
        if updated or not _args.update:
            outfile.write(ET.tostring(elem, encoding='us-ascii'))
    outfile.write(b'</Interchange>')
    for idnum in newlocs:
        trace(1, 'In CSV but not XML: {}', idnum)


def getargs():
    parser = argparse.ArgumentParser(description='''
        Set the normal location and/or current location to the new location
        from a CSV file with rows of the format: <object number>,<location>.
        If the location in the CSV file differs from the location in the XML
        file, update the Date/DateBegin element to today's date unless the
        --date option is specified.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-b', '--both', action='store_true', help='''
        Update both the current location and the normal location.
        Select one of "b", "n", and "c".''')
    parser.add_argument('-c', '--current', action='store_true', help='''
        Update the current location.
        Select one of "b", "n", and "c".''')
    parser.add_argument('-d', '--date', default=today, help='''
        Use this string as the date to store in the new ObjectLocation date.
        The default is today's date in ISO format.
        ''')
    parser.add_argument('-n', '--normal', action='store_true', help='''
        Update the normal location.
        Select one of "b", "n", and "c".''')
    parser.add_argument('-u', '--update', action='store_true', help='''
        Only write changed objects. The default is to write all objects and
        issue a warning if an object is not in the detail CSV file.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-m', '--mapfile', required=True, help='''
        The CSV file mapping the object number to its location''')
    args = parser.parse_args()
    if int(args.both) + int(args.current) + int(args.normal) != 1:
        raise ValueError('Select one of "b", "n", and "c".')
    args.current |= args.both
    args.normal |= args.both
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    today = nd.modesdate(date.today())
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    newlocs = loadlocs()
    main()
