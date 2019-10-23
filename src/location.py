# -*- coding: utf-8 -*-
"""
Utility for handling object location updating and checking.

"""
import argparse
import codecs
import csv
from datetime import date
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl import normalize_date


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
            location_dict[row[0].strip()] = row[_args.col].strip()
    return location_dict


def handle_check(idnum, elem):
    if _args.all:
        if idnum not in newlocs:
            trace(3, 'Not in CSV file: {}', idnum)
        return
    objlocs = elem.findall('./ObjectLocation')
    for ol in objlocs:
        loc = ol.get('elementtype')
        if (_args.normal and loc == 'normal location') or (
                _args.current and loc == 'current location'
        ):
            location = ol.find('./Location')
            if location.text is not None:
                text = location.text.strip().upper()
            else:
                text = None
            newtext = newlocs[idnum]  # we've checked that it's there
            trace(2, 'Found in CSV {}: {}', idnum, newtext)
            if text != newtext:
                trace(1, 'Different {}: XML: {}, CSV: {}', idnum, text,
                      newtext)
            break
    del newlocs[idnum]


def update_one_location(ol, idnum):
    """
    If the location in the newlocs dictionary is different from the location
    in the XML, update the XML, insert the date specified on the command line,
    and delete the idnum from the global "newlocs" dictionary.
    Note that we have already tested that idnum is in newlocs.

    :param ol: the ObjectLocation element
    :param idnum: the ObjectIdentity/Number text
    :return: True if the object is updated, False otherwise
    """
    global total_updated
    updated = False
    location = ol.find('./Location')
    if location.text is not None:
        text = location.text.strip().upper()
    else:
        text = None
    newtext = newlocs[idnum]  # we've already checked that it's there
    if text != newtext:
        trace(2, '{}: Updated {} -> {}', idnum, text, newtext)
        location.text = newtext
        datebegin = ol.find('./Date/DateBegin')
        if datebegin is not None:  # normal location doesn't have a date
            datebegin.text = _args.date
        updated = True
        total_updated += 1
    else:
        trace(2, 'Unchanged: {}: {}', idnum, text)
    return updated


def handle_update(idnum, elem):
    global total_written
    updated = False
    if idnum in newlocs:
        objlocs = elem.findall('./ObjectLocation')
        gotloc = False
        for ol in objlocs:
            loc = ol.get('elementtype')
            if (_args.normal and loc == 'normal location') or (
                    _args.current and loc == 'current location'
            ):
                gotloc = True
                updated = update_one_location(ol, idnum)
        if not gotloc:  # cannot find correct elementtype in XML
            trace(1, '{}: Specified object location missing', idnum)
        del newlocs[idnum]
    else:
        if _args.all:
            trace(3, '{}: Not in CSV file', idnum)
    if updated or _args.all:
        outfile.write(ET.tostring(elem, encoding='us-ascii'))
        total_written += 1


def main():
    outfile.write(b'<?xml version="1.0" encoding="utf-8"?><Interchange>\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find('./ObjectIdentity/Number')
        idnum = idelem.text if idelem is not None else None
        trace(3, 'idnum: {}', idnum)
        _args.func(idnum, elem)  # handle_check() or handle_update()
    outfile.write(b'</Interchange>')
    for idnum in newlocs:
        trace(1, '{}: In CSV but not XML', idnum)


def add_arguments(parser):
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    if is_update:
        parser.add_argument('outfile', help='''
            The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects and issue a warning if an object is not in the detail
        CSV file. The default is to only write updated objects. In either case
        warn if an object in the CSV file is not in the input XML file.
        ''')
    if is_update:
        parser.add_argument('-b', '--both', action='store_true', help='''
            Update both the current location and the normal location.
            Select one of "b", "n", and "c".''')
    parser.add_argument('--col', type=int, default=1, help='''
        Specify the column in the CSV file containing the location.
        Default is 1 (first column is zero).
        ''')
    parser.add_argument('-c', '--current', action='store_true', help='''
        Update the current location.
        Select one of "b", "n", and "c".''')
    if is_update:
        parser.add_argument('-d', '--date', default=today, help='''
            Use this string as the date to store in the new ObjectLocation
            date. The default is today's date in Modes format (d.m.y).
            ''')
    parser.add_argument('--encoding', default='utf-8', help='''
        Set the input encoding. Default is utf-8. Output is always ascii.
        ''')
    parser.add_argument('-n', '--normal', action='store_true', help='''
        Update the normal location.
        Select one of "b", "n", and "c".''')
    if is_check:
        parser.add_argument('--old', action='store_true', help='''
            The column selected is the "old" location, the one we are moving
            the object from. Warn if the value in the CSV file does not match
            the value in the XML file. The default is to warn if the value in
            the CSV file does match the value in the XML file which is not
            expected as the purpose is to update that value.
            You must select either --normal or --current, not --both.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-m', '--mapfile', required=True, help='''
        The CSV file mapping the object number to its location. The object ID
        is in the first column (column 0). The new location is by default
        in the second column (column 1) but can be changed by the --col option.
        ''')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Set the normal location and/or current location to the new location
        from a CSV file with rows of the format: <object number>,<location>.
        If the location in the CSV file differs from the location in the XML
        file, update the Date/DateBegin element to today's date unless the
        --date option is specified.
        ''')
    subparsers = parser.add_subparsers(dest='subp')
    check_parser = subparsers.add_parser('check', description='''
    With no options, check that the location in the object specified by --col
    is the same as the location specified by -c or -n option in the XML file.
    ''')
    update_parser = subparsers.add_parser('update', description='''
    Update the XML file from the location in the CSV file specified by -m.
    ''')
    check_parser.set_defaults(func=handle_check)
    update_parser.set_defaults(func=handle_update)
    add_arguments(check_parser)
    add_arguments(update_parser)
    args = parser.parse_args()
    if int(args.both) + int(args.current) + int(args.normal) != 1:
        raise ValueError('Select one of "b", "n", and "c".')
    args.current |= args.both
    args.normal |= args.both
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    is_update = sys.argv[1] == 'update'
    is_check = sys.argv[1] == 'check'
    today = normalize_date.modesdate(date.today())  # '[d]d.[m]m.yyyy'
    _args = getargs()
    infile = open(_args.infile, encoding=_args.encoding)
    newlocs = loadlocs()
    total_updated = 0
    total_written = 0
    if is_update:
        outfile = open(_args.outfile, 'wb')
    main()
    if is_update:
        print(f'Total Updated: {total_updated}, Total Written: {total_written}')
