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
import utl.normalize_date as nd

NORMAL_LOCATION = 'normal location'
CURRENT_LOCATION = 'current location'
ELEMENTTYPE = 'elementtype'

verbose = 1  # overwritten by _args.verbose; set here for unittest


def trace(level, template, *args):
    if verbose >= level:
        print(template.format(*args))


def loadcsv():
    """
    Read the CSV file containing objectid -> location mappings
    :return: the dictionary containing the mappings
    """
    location_dict = {}
    if _args.subp == 'validate':
        return location_dict
    loc_arg = _args.location
    need_heading = bool(_args.heading)
    with codecs.open(_args.mapfile, 'r', 'utf-8-sig') as mapfile:
        reader = csv.reader(mapfile)
        for row in reader:
            if need_heading:
                # if --location is given just skip the first row
                if not loc_arg and (row[_args.col].strip().lower()
                                    != _args.heading.lower()):
                    print(f'Failed heading check. {row[_args.col].lower()} is not '
                          f'{_args.heading.lower()}')
                    sys.exit(1)
                need_heading = False
                continue
            location_dict[row[0].strip()] = loc_arg if loc_arg else row[_args.col].strip()
    return location_dict


def handle_check(idnum, elem):
    if _args.all:
        if idnum not in newlocs and _args.warn:
            trace(3, 'Not in CSV file: {}', idnum)
            return
    objlocs = elem.findall('./ObjectLocation')
    for ol in objlocs:
        loc = ol.get(ELEMENTTYPE)
        if (_args.normal and loc == NORMAL_LOCATION) or (
                _args.current and loc == CURRENT_LOCATION
        ):
            location = ol.find('./Location')
            if location.text is not None:
                text = location.text.strip().upper()
            else:
                text = None
            newtext = _args.location if _args.location else newlocs[idnum]
            trace(2, 'New location for {}: {}', idnum, newtext)
            if text != newtext:
                trace(1, 'Different {}: XML: {}, CSV: {}', idnum, text,
                      newtext)
            break
    del newlocs[idnum]


def validate_locations(idnum, elem):
    """
    :param idnum:
    :param elem: The Object element
    :return: True if valid, False otherwise
    """
    numnormal = numcurrent = 0
    numnodateend = 0
    objlocs = elem.findall('./ObjectLocation')
    currentlocs = []
    for ol in objlocs:
        loc = ol.get(ELEMENTTYPE)
        if loc == NORMAL_LOCATION:
            numnormal += 1
        elif loc == CURRENT_LOCATION:
            numcurrent += 1
            datebegin = ol.find('./Date/DateBegin')
            if datebegin is None or datebegin.text is None:
                trace(1, 'E01 {}: No DateBegin for current location', idnum)
                return False
            try:
                datebegindate = nd.date(datebegin.text)
            except (ValueError, TypeError):
                trace(1,'E02 {}: Invalid DateBegin for current location: "{}".', idnum,
                      datebegin.text)
                return False
            dateend = ol.find('./Date/DateEnd')
            if dateend is None or dateend.text is None:
                numnodateend += 1
                dateenddate = None
            else:
                try:
                    dateenddate = nd.date(dateend.text)
                except (ValueError, TypeError):
                    trace(1, 'E03 {}: Invalid DateEnd for current location: "{}".', idnum,
                          dateend.text)
                    return False
            currentlocs.append((datebegindate, dateenddate))
        else:
            trace(1, 'E04 {}: Unexpected ObjectLocation elementtype = "{}".', idnum, loc)
            return False
    if numnormal != 1:
        trace(1, 'E05 {}: Expected one normal location, got {}', idnum, numnormal)
        return False
    if numcurrent < 1:
        trace(1, 'E06 {}: Expected one or more current locations, got 0', idnum)
        return False
    if numnodateend != 1:
        trace(1, 'E07 {}: Expected one current location with no DateEnd, got {}', idnum,
              numnodateend)
        return False

    # Check that the latest date is the one with no DateEnd.
    currentlocs.sort(reverse=True)
    if currentlocs[0][1] is not None:
        trace(1, 'E08 {}: current location with no DateEnd is not the latest.', idnum)
        return False
    if len(currentlocs) > 1:
        prevbegin, prevend = currentlocs[0]
        for nxtbegin, nxtend in currentlocs[1:]:
            if nxtend < nxtbegin:
                trace(1, 'E09 {}: begin date {} is younger than end date {}.', idnum,
                      nxtbegin.isoformat(), nxtend.isoformat())
                return False
            if nxtend != prevbegin:
                trace(1, 'E10 {}: begin date "{}" not equal to previous end date "{}".',
                      idnum, str(prevbegin), str(nxtend))
                return False
            prevbegin = nxtbegin
    return True


def update_normal_location(ol, idnum):
    """
    :param ol: the ObjectLocation element
    :param idnum: the ObjectIdentity/Number text (we've tested that idnum is in newlocs)
    :return: True if the object is updated, False otherwise
    """
    updated = False
    location = ol.find('./Location')
    if location.text is not None:
        text = location.text.strip().upper()
    else:
        text = None

    newtext = _args.location if _args.location else newlocs[idnum]
    if text != newtext:
        trace(2, '{}: Updated normal location {} -> {}', idnum, text, newtext)
        location.text = newtext
        updated = True
    else:
        trace(2, 'Normal location unchanged: {}: {}', idnum, text)
    return updated


def update_current_location(elem, idnum):
    """

    :param elem: the Object element
    :param idnum: the ObjectIdentity/Number text (we've tested that idnum is in newlocs)
    :return: True if the object is updated, False otherwise

    Insert a new current location element. If --reset_current is set, delete all of the
    existing current location elements.

    The order of the ObjectLocation elements is that the first one in the document is
    the normal location followed by the current location elements with the newest ones
    first.

    """
    subelts = list(elem)
    normlocix = 0
    objlocfound = False
    for elt in subelts:
        normlocix += 1
        if elt.tag == 'ObjectLocation':
            objlocfound = True
            break
    if not objlocfound:
        trace(1, '{}: Cannot find ObjectLocation', idnum)
        return False
    # normlocix is the index of the normal location (first index is 1). This is where we
    # will insert the new current location element.

    # Update the existing current location to have a DateEnd element
    currentlocelem = elem.find('./ObjectLocation[2]')
    locationelt = currentlocelem.find('./Location')
    if locationelt.text is not None:
        text = locationelt.text.strip().upper()
    else:
        text = None
    newlocation = _args.location if _args.location else newlocs[idnum]
    if text == newlocation.upper():
        trace(2, 'Unchanged: {}: {}', idnum, text)
        return False
    oldate = currentlocelem.find('./Date')
    ET.SubElement(oldate, 'DateEnd').text = _args.date

    # Insert a new ObjectLocation after the normal location
    newloc = ET.Element('ObjectLocation')
    newloc.set(ELEMENTTYPE, CURRENT_LOCATION)
    ET.SubElement(newloc, 'Location').text = newlocation
    locdate = ET.SubElement(newloc, 'Date')
    ET.SubElement(locdate, 'DateBegin').text = _args.date
    ET.SubElement(newloc, 'Reason').text = _args.reason
    elem.insert(normlocix, newloc)  # insert the new element after the normal location
    trace(2, '{}: Updated {} -> {}', idnum, text, newlocation)
    return True


def handle_update(idnum, elem):
    """
    If the location in the newlocs dictionary is different from the location
    in the XML, update the XML, insert the date specified on the command line,
    and delete the idnum from the global "newlocs" dictionary.

    :param idnum:
    :param elem:
    :return: None
    """
    global total_updated, total_written
    updated = False
    if idnum in newlocs:
        if not validate_locations(idnum, elem):
            trace(1, 'Failed pre-update validation.')
            sys.exit(1)
        if _args.normal:
            objlocs = elem.findall('./ObjectLocation')
            for ol in objlocs:
                loc = ol.get('elementtype')
                if loc == NORMAL_LOCATION:
                    updated = update_normal_location(ol, idnum)
                    break
        if _args.current:
            updated = update_current_location(elem, idnum)
        del newlocs[idnum]
    else:
        if _args.warn:
            trace(1, '{}: Not in CSV file', idnum)
    if idnum in newlocs and not validate_locations(idnum, elem):
        trace(1, 'Failed post-update validation.')
        sys.exit(1)
    if updated:
        total_updated += 1
    if updated or _args.all:
        outfile.write(ET.tostring(elem, encoding='us-ascii'))
        total_written += 1


def handle_validate(idnum, elem):
    global total_failed, total_objects
    total_objects += 1
    valid = validate_locations(idnum, elem)
    if not valid:
        total_failed += 1


def main():
    if outfile:
        outfile.write(b'<?xml version="1.0" encoding="utf-8"?><Interchange>\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find('./ObjectIdentity/Number')
        idnum = idelem.text if idelem is not None else None
        trace(3, 'idnum: {}', idnum)
        _args.func(idnum, elem)  # handle_check() or handle_update() or handle_validate()
        if _args.short:
            break
    if outfile:
        outfile.write(b'</Interchange>')
    if not _args.short:  # Skip warning if only processing one object.
        for idnum in newlocs:
            trace(1, '{}: In CSV but not XML', idnum)


def add_arguments(parser):
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    if is_update:
        parser.add_argument('outfile', help='''
            The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects and, if -w is selected, issue a warning if an object is not in
        the detail CSV file. The default is to only write updated objects. In either case
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
        parser.add_argument('-d', '--date', default=nd.modesdate(date.today()), help='''
            Use this string as the date to store in the new ObjectLocation
            date. The default is today's date in Modes format (d.m.yyyy).
            ''')
    parser.add_argument('--encoding', default='utf-8', help='''
        Set the input encoding. Default is utf-8. Output is always ascii.
        ''')
    parser.add_argument('--heading', help='''
        The first row of the map file contains a heading which must match the parameter
        (case insensitive).
        ''')
    parser.add_argument('-l', '--location', help='''
        Set the location for all of the objects. In this case the CSV file only needs a
        single column containing the accession number.
        ''')
    if is_check or is_update:
        parser.add_argument('-m', '--mapfile', required=True, help='''
            The CSV file mapping the object number to its new location. The object ID
            is in the first column (column 0). The new location is by default
            in the second column (column 1) but can be changed by the --col option.
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
            ''')
    if is_update:
        parser.add_argument('--reset_current', action='store_true', help='''
        Only output the most recent current location element for each object.
        ''')
        parser.add_argument('-r', '--reason', default='', help='''
            Insert this text as the reason for the move to the new current location.
            ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process a single object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-w', '--warn', action='store_true', help='''
        Valid if -a is selected. Warn if an object in the XML file is not in the CSV file.
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
    validate_parser = subparsers.add_parser('validate', description='''
    Run the validate_locations function against the input file.
    ''')
    check_parser.set_defaults(func=handle_check)
    update_parser.set_defaults(func=handle_update)
    validate_parser.set_defaults(func=handle_validate)
    add_arguments(check_parser)
    add_arguments(update_parser)
    add_arguments(validate_parser)
    args = parser.parse_args()
    if is_check or is_update:
        if int(args.both) + int(args.current) + int(args.normal) != 1:
            raise ValueError('Select one of "b", "n", and "c".')
        args.current |= args.both
        args.normal |= args.both
        # Set a fake value for the new location column as it will be taken from the --location
        # value instead of a column in the CSV file.
        if args.location:
            args.col = None
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    is_update = sys.argv[1] == 'update'
    is_check = sys.argv[1] == 'check'
    is_validate = sys.argv[1] == 'validate'
    _args = getargs()
    verbose = _args.verbose
    infile = open(_args.infile, encoding=_args.encoding)
    newlocs = loadcsv()
    total_in_csvfile = len(newlocs)
    total_updated = total_written = 0
    total_failed = total_objects = 0  # validate only
    if is_update:
        outfile = open(_args.outfile, 'wb')
    else:
        outfile = None
    main()
    if is_update:
        print(f'Total Updated: {total_updated}/{total_in_csvfile}\n'
              f'Total Written: {total_written}')
    if is_validate:
        print(f'Total failed: {total_failed}/{total_objects}.')
    trace(1, 'End location {}.', _args.subp)
