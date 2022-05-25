# -*- coding: utf-8 -*-
"""
Utility for handling object location updating and checking.

There are three location types recorded in the XML database, the normal,
current, and previous locations. There may be multiple previous locations. The
input CSV file (the "map" file) only applies to one of these location types. So
if you need to update multiple types, you must prepare separate input CSV files
and run this program more than once.

Exception: When updating a current location, a previous location element is
created (unless the --patch option is selected).
"""
import argparse
import codecs
import csv
from datetime import date
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
import utl.normalize as nd
from utl.cfgutil import expand_idnum

NORMAL_LOCATION = 'normal location'
CURRENT_LOCATION = 'current location'
PREVIOUS_LOCATION = 'previous location'
ELEMENTTYPE = 'elementtype'

verbose = 1  # overwritten by _args.verbose; set here for unittest


def trace(level, template, *args):
    if verbose >= level:
        print(template.format(*args))


def loadcsv():
    """
    Read the CSV file containing objectid -> location mappings, specified
    by the --mapfile argument.
    :return: the dictionary containing the mappings
    """
    rownum = 0
    location_dict, reason_dict = {}, {}
    if _args.subp == 'validate':
        return location_dict, reason_dict
    loc_arg = _args.location
    need_heading = bool(_args.heading)
    with codecs.open(_args.mapfile, 'r', 'utf-8-sig') as mapfile:
        reader = csv.reader(mapfile)
        for n in range(_args.skiprows):
            next(reader)
        for row in reader:
            rownum += 1
            trace(3, 'row: {}', row)
            if need_heading:
                # if --location is given just skip the first row
                if not loc_arg and (row[_args.col_loc].strip().lower()
                                    != _args.heading.lower()):
                    print(f'Fatal error: Failed heading check. '
                          f'{row[_args.col_loc].lower()} is not '
                          f'{_args.heading.lower()}.')
                    sys.exit(1)
                need_heading = False
                continue
            objid = row[_args.col_acc].strip().upper()
            if not objid:
                if ''.join(row):
                    trace(2, 'Skipping row with blank object id: {}', row)
                continue
            objidlist = expand_idnum(objid)
            reason = ''
            if is_update:
                if _args.reason:
                    reason = _args.reason
                elif _args.col_reason:
                    reason = row[_args.col_reason]
            location = loc_arg if loc_arg else row[_args.col_loc].strip()
            for ob in objidlist:
                nobjid = nd.normalize_id(ob)
                if not nobjid:
                    print(f'Warning: Blank object ID row {rownum}: {row}')
                    continue  # blank number
                if nobjid in location_dict:
                    print(f'Fatal error: Duplicate object ID row {rownum}: {row}.')
                    sys.exit(1)
                location_dict[nobjid] = location
                reason_dict[nobjid] = reason
    return location_dict, reason_dict


def handle_diff(idnum, elem):
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
            if _args.location:
                newtext = _args.location
            else:
                nidnum = nd.normalize_id(idnum)
                newtext = newlocs.get(nidnum, None)
                if newtext is None:
                    return
                del newlocs[nidnum]
            trace(2, 'New location for {}: {}', idnum, newtext)
            if text != newtext:
                trace(1, 'Different {}: XML: {}, CSV: {}', idnum, text,
                      newtext)
            break


def validate_locations(idnum, elem, strict=True):
    """
    :param idnum:
    :param elem: The Object element
    :param strict: If False, allow gaps in the dates of the current and previous locations
    :return: True if valid, False otherwise
    """
    numnormal = numcurrent = 0
    objlocs = elem.findall('./ObjectLocation')
    locationdates = []
    for ol in objlocs:
        datebegin = ol.find('./Date/DateBegin')
        dateend = ol.find('./Date/DateEnd')
        loctype = ol.get(ELEMENTTYPE)
        if loctype == NORMAL_LOCATION:
            numnormal += 1
        elif loctype == CURRENT_LOCATION:
            loc = ol.find('./Location')
            if loc is None:
                trace(1, 'E10 {}: Missing ObjectLocation/Location element',
                      idnum)
                return False
            # Skip the validation if the current location is empty. This can
            # happen after adding a new object.
            if not loc.text:
                return True
            numcurrent += 1
            if datebegin is None or datebegin.text is None:
                trace(1, 'E01 {}: No DateBegin for current location', idnum)
                return False
            try:
                datebegindate, _ = nd.datefrommodes(datebegin.text)
            except (ValueError, TypeError):
                trace(1,
                      'E02 {}: Invalid DateBegin for current location: "{}".',
                      idnum, datebegin.text)
                return False
            if dateend is not None and dateend.text is not None:
                trace(1,
                      'E03 {}: DateEnd not allowed for current location: "{}".',
                      idnum, dateend.text)
                return False
            locationdates.append((datebegindate, None))  # None indicates this is current
        elif loctype == PREVIOUS_LOCATION:
            try:
                datebegindate, _ = nd.datefrommodes(datebegin.text)
            except (ValueError, TypeError):
                trace(1,
                      'E04 {}: Invalid DateBegin for previous location: "{}".',
                      idnum, datebegin.text)
                return False
            if dateend is None or dateend.text is None:
                trace(1, 'E05 {}: Missing DateEnd for previous location.',
                      idnum)
                return False
            try:
                dateenddate, _ = nd.datefrommodes(dateend.text)
            except (ValueError, TypeError):
                trace(1,
                      'E06 {}: Invalid DateEnd for previous location: "{}".',
                      idnum, dateend.text)
                return False
            locationdates.append((datebegindate, dateenddate))
        else:
            trace(1, 'E07 {}: Unexpected ObjectLocation elementtype = "{}".',
                  idnum, loctype)
            return False
    if numnormal != 1:
        trace(1, 'E08 {}: Expected one normal location, got {}',
              idnum, numnormal)
        return False
    if numcurrent != 1:
        trace(1, 'E09 {}: Expected one current location, got {}',
              idnum, numcurrent)
        return False
    if len(locationdates) == 1:
        return True  # There are no previous locations

    # Check that the youngest date is the current location and that there is no overlap.
    locationdates.sort(reverse=True)
    if locationdates[0][1] is not None:  # should not have an end date
        trace(1, 'E08 {}: current location is not the youngest.', idnum)
        return False
    prevbegin, prevend = locationdates[0]
    for nxtbegin, nxtend in locationdates[1:]:
        if nxtend < nxtbegin:
            trace(1, 'E09 {}: end date {} is younger than begin date {}.', idnum,
                  nxtbegin.isoformat(), nxtend.isoformat())
            return False
        if nxtend != prevbegin:
            if strict:
                trace(1, 'E10 {}: begin date "{}" not equal to previous end date "{}".',
                      idnum, str(prevbegin), str(nxtend))
                return False
            elif nxtend > prevbegin:
                trace(1, 'E11 {}: Younger begin date "{}" overlaps with end date. "{}".',
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

    nidnum = nd.normalize_id(idnum)
    newtext = _args.location if _args.location else newlocs[nidnum]
    if text != newtext:
        trace(2, '{}: Updated normal {} -> {}', idnum, text, newtext)
        location.text = newtext
        updated = True
    else:
        trace(2, '{}: Normal location unchanged: {}', idnum, text)
    return updated


def update_current_location(elem, idnum):
    """

    :param elem: the Object element
    :param idnum: the ObjectIdentity/Number text (we've tested that idnum is in
     newlocs)
    :return: True if the object is updated, False otherwise

    If --patch is set, change the date on the current location. Otherwise,
    change the current location into a previous location and insert a new
    current location element.

    If --reset_current is set, delete all the existing previous location elements.

    We've called validate_locations() so there is no need to test return
    values from function calls.

    """

    # Find the current location
    ol = elem.find('./ObjectLocation[@elementtype="current location"]')

    # If the location hasn't changed, do nothing.
    locationelt = ol.find('./Location')
    if locationelt.text is not None:
        oldlocation = locationelt.text.strip().upper()
    else:
        oldlocation = None
    nidnum = nd.normalize_id(idnum)
    newlocationtext = _args.location if _args.location else newlocs[nidnum]

    # If the current location is empty, just insert the new location without
    # creating a previous location.
    if not oldlocation:
        trace(2, 'Inserting location into empty current location: {}: {}',
              idnum, newlocationtext)
        locationelt.text = newlocationtext
        datebegin = ol.find('./Date/DateBegin')
        datebegin.text = _args.date
        return True
    if oldlocation == newlocationtext.upper():
        trace(2, 'Unchanged: {}: {}', idnum, oldlocation)
        if _args.force:
            return True
        else:
            return False

    if _args.patch:
        datebegin = ol.find('./Date/DateBegin')
        oldlocation = ol.find('./Location')
        datebegin.text = _args.date
        oldlocationtext = oldlocation.text
        oldlocation.text = newlocationtext
        oldreason = ol.find('./Reason')
        reasontext = _args.reason if _args.reason else 'Patched'
        if oldreason is not None:
            oldreason.text = reasontext
        else:
            ET.SubElement(ol, 'Reason').text = reasontext

        trace(2, '{}: Patched current location {} -> {}', idnum, oldlocationtext,
              newlocationtext)
        return True

    # Create the new current location element.
    newobjloc = ET.Element('ObjectLocation')
    newobjloc.set(ELEMENTTYPE, CURRENT_LOCATION)
    ET.SubElement(newobjloc, 'Location').text = newlocationtext
    locdate = ET.SubElement(newobjloc, 'Date')
    ET.SubElement(locdate, 'DateBegin').text = _args.date
    ET.SubElement(newobjloc, 'Reason').text = newreasons[nidnum]

    # Find the current location's index
    subelts = list(elem)
    clix = 0  # index of the current location
    for elt in subelts:
        clix += 1
        if elt.tag == 'ObjectLocation' and elt.get(ELEMENTTYPE) == CURRENT_LOCATION:
            break

    # Insert the DateEnd text in the existing current location and convert it to a
    # previous location
    oldate = ol.find('./Date')
    oldateend = oldate.find('./DateEnd')
    if oldateend is None:
        oldateend = ET.SubElement(oldate, 'DateEnd')
    oldateend.text = _args.date
    ol.set(ELEMENTTYPE, PREVIOUS_LOCATION)

    # insert the new current location before the old current location (which is
    # now a previous location.
    elem.insert(clix - 1, newobjloc)

    if _args.reset_current:
        subelts = elem.findall('./ObjectLocation')
        for elt in subelts:
            if elt.get(ELEMENTTYPE) == PREVIOUS_LOCATION:
                trace(2, 'Removing previous location from {}.', idnum)
                elem.remove(elt)

    trace(2, '{}: Updated current {} -> {}', idnum, oldlocation, newlocationtext)
    return True


def update_previous_location(elem, idnum):
    print(f'Update of previous location not implemented. {elem=} {idnum=}')
    sys.exit(1)


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
    nidnum = nd.normalize_id(idnum)
    if nidnum in newlocs:  # newlocs: list returned by loadcsv()
        if not validate_locations(idnum, elem):
            trace(1, 'Failed pre-update validation.')
            sys.exit(1)
        if _args.normal:
            ol = elem.find('./ObjectLocation[@elementtype="normal location"]')
            updated = update_normal_location(ol, idnum)
        if _args.current:
            updated |= update_current_location(elem, idnum)
        if _args.previous:
            updated |= update_previous_location(elem, idnum)
        del newlocs[nidnum]
    else:
        if _args.warn:
            trace(1, '{}: Not in CSV file', idnum)
    if nidnum in newlocs and not validate_locations(idnum, elem):
        trace(1, 'Failed post-update validation.')
        sys.exit(1)
    if updated:
        total_updated += 1
    if updated or _args.all:
        outfile.write(ET.tostring(elem, encoding='utf-8'))
        total_written += 1


def handle_validate(idnum, elem):
    global total_failed, total_objects
    total_objects += 1
    valid = validate_locations(idnum, elem)
    if not valid:
        total_failed += 1


def handle_select(idnum, elem):
    if idnum in newlocs:  # newlocs: list returned by loadcsv()
        del newlocs[idnum]
        outfile.write(ET.tostring(elem, encoding='utf-8'))
    return


def main():
    if outfile:
        outfile.write(b'<?xml version="1.0" encoding="utf-8"?><Interchange>\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find('./ObjectIdentity/Number')
        idnum = idelem.text.upper() if idelem is not None else None
        trace(3, 'idnum: {}', idnum)
        _args.func(idnum, elem)  # handle_diff() or handle_update() or handle_validate()
        if _args.short:
            break
    if outfile:
        outfile.write(b'</Interchange>')
    if not _args.short:  # Skip warning if only processing one object.
        for idnum in newlocs:
            trace(1, '{}: In CSV but not XML', idnum)


def add_arguments(parser, command):
    global is_update, is_diff, is_select, is_validate  # Needed for Sphinx
    reason_group = None  # stop PyCharm whining
    if called_from_sphinx:
        is_update = command == 'update'
        is_diff = command == 'diff'
        is_select = command == 'select'
        is_validate = command == 'validate'
    parser.add_argument('-i', '--infile', required=True, help='''
        The XML file saved from Modes.''')
    if is_update or is_select:
        parser.add_argument('-o', '--outfile', required=True, help='''
            The output XML file.''')
    if is_update or is_select:
        parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects and, if -w is selected, issue a warning if an object
        is not in the detail CSV file. The default is to only write updated
        objects. In either case warn if an object in the CSV file is not in the
        input XML file.''')
    if is_update or is_diff:
        parser.add_argument('--col_acc', type=int, default=0, help='''
        The zero-based column containing the accession number of the
        object to be updated. The default is column zero.
        ''')
        parser.add_argument('--col_loc', type=int, default=1,
                            help=nd.sphinxify('''
        The zero-based column containing the new location of the
        object to be updated. The default is column 1. See the --location
        option which sets the location for all objects in which case this
        option is ignored.''', called_from_sphinx))
    if is_update:
        reason_group = parser.add_mutually_exclusive_group()
        reason_group.add_argument('--col_reason', help=nd.sphinxify('''
            The zero-based column containing text to be inserted as the
            reason for the move to the new current location for the object
            named in the row. Specify this or --reason.
            ''', called_from_sphinx))
    if is_update or is_diff:
        parser.add_argument('-c', '--current', action='store_true', help='''
        Update the current location and change the old current location to a
        previous location. See the descrption of "n" and "p". ''')
    if is_update:
        parser.add_argument('-d', '--date', default=nd.modesdate(date.today()), help='''
            When updating the current location, use this date as the DateEnd
            value for the previous location we're making and the DateBegin
            value for the new current location we're making. The default is
            today's date in Modes format (d.m.yyyy).
            ''')
        parser.add_argument('--datebegin', help='''
        Use this string as the date to store in the new previous ObjectLocation
        date. The format must be in Modes format (d.m.yyyy).
        ''')
        parser.add_argument('--dateend', default=nd.modesdate(date.today()),
                            help='''
        Use this string as the date to store in the new previous ObjectLocation
        date. The format must be in Modes format (d.m.yyyy).
        ''')
    parser.add_argument('--encoding', default='utf-8', help='''
        Set the input encoding. Default is utf-8. Output is always utf-8.
        ''')
    if is_update:
        parser.add_argument('-f', '--force', action='store_true', help='''
        Write the object to the output file even if it hasn't been updated. This only
        applies to objects whose ID appears in the CSV file. -a implies -f.
        ''')
    parser.add_argument('--heading', help=nd.sphinxify('''
        The first row of the map file contains a column title which must match the
        parameter (case insensitive) in the column designated for the location.
        If a --location argument is specified, the first row is skipped and the
        value, which nevertheless must be specified, is ignored. 
        ''', called_from_sphinx))
    if is_update or is_diff or is_select:
        map_group = parser.add_mutually_exclusive_group(required=True)
        map_group.add_argument('-j', '--object', help=nd.sphinxify('''
        Specify a single object to be processed. If specified, do not specify
        the CSV file containing object numbers and locations (--mapfile). You
        must also specify --location.
        ''', called_from_sphinx))
        parser.add_argument('-l', '--location', help='''
        Set the location for all of the objects in the CSV file. In this 
        case the CSV file only needs a single column containing the 
        accession number.  
        ''')
        map_group.add_argument('-m', '--mapfile', help=nd.sphinxify('''
            The CSV file mapping the object number to its new location. By
            default, the accession number is in the first column (column 0) but 
            this can be changed by the --col_acc option. The new location is by
            default in the second column (column 1) but can be changed by the
            --col_loc option. This  argument is ignored if --object is specified.
            ''', called_from_sphinx))
    if is_update or is_diff:
        parser.add_argument('-n', '--normal', action='store_true', help='''
        Update the normal location. See the description for "p" and "c".''')
    if is_diff:
        parser.add_argument('--old', action='store_true', help='''
            The column selected is the "old" location, the one we are moving
            the object from. Warn if the value in the CSV file does not match
            the value in the XML file. The default is to warn if the value in
            the CSV file does match the value in the XML file which is not
            expected as the purpose is to update that value.
            ''')
    if is_update:
        parser.add_argument('--patch', action='store_true', help='''
        Update the specified location in place without creating history. This
        is always the behavior for normal locations but not for current or
        previous.
        ''')
        parser.add_argument('-p', '--previous', action='store_true',
                            help=nd.sphinxify('''
        Add a previous location. This location's start and end dates must 
        not overlap with an existing current or previous location's date(s). 
        If "p" is selected, do not select "n" or "c". If "p" is specified, you
        must specify --datebegin and --dateend.
        ''', called_from_sphinx))
        parser.add_argument('--reset_current', action='store_true', help='''
        Only output the most recent current location element for each object,
        deleting all previous locations.
        ''')
        reason_group.add_argument('-r', '--reason', default='',
                                  help=nd.sphinxify('''
            Insert this text as the reason for the move to the new current
            location for all of the objects updated. Specify this or
            --col_reason.
            ''', called_from_sphinx))
    parser.add_argument('--short', action='store_true', help='''
        Only process a single object. For debugging.''')
    parser.add_argument('-s', '--skiprows', type=int, default=0, help='''
        Number of lines to skip at the start of the CSV file''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    if is_diff or is_select or is_update:
        parser.add_argument('-w', '--warn', action='store_true', help='''
        Valid if -a is selected. Warn if an object in the XML file is not in
        the CSV file.
        ''')


def getparser():
    parser = argparse.ArgumentParser(description=nd.sphinxify('''
        Set the normal location and/or current location to the new location
        from a CSV file with rows of the format: <object number>,<location>.
        If the location in the CSV file differs from the location in the XML
        file, update the ``Date/DateBegin`` element to today's date unless the
        --date option is specified. If a new current location is being set,
        create a previous location from the existing current location.
        ''', called_from_sphinx))
    subparsers = parser.add_subparsers(dest='subp')
    diff_parser = subparsers.add_parser('diff', description=nd.sphinxify('''
    With no options, compare the location of the object in the mapfile as
    specified by --col_loc
    to either the normal or current location as specified by -c or -n option in
    the XML file.
    ''', called_from_sphinx))
    select_parser = subparsers.add_parser('select', description='''
    Select the objects named in the CSV file specified by -m and write them to
    the output without modification. 
    ''')
    update_parser = subparsers.add_parser('update', description='''
    Update the XML file from the location in the CSV file specified by -m.
    ''')
    validate_parser = subparsers.add_parser('validate', description='''
    Run the validate_locations function against the input file. This validates
    all locations and ignores the -c, -n, and -p options. This checks that
    dates exist and do not overlap.
    ''')
    diff_parser.set_defaults(func=handle_diff)
    select_parser.set_defaults(func=handle_select)
    update_parser.set_defaults(func=handle_update)
    validate_parser.set_defaults(func=handle_validate)
    add_arguments(diff_parser, 'diff')
    add_arguments(select_parser, 'select')
    add_arguments(update_parser, 'update')
    add_arguments(validate_parser, 'validate')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if is_update:
        nloctypes = int(args.current) + int(args.previous)
        if nloctypes != 1:
            print('Exactly one of -c or -p must be specified.')
            sys.exit(1)
        if not nd.vdate(args.date):
            print('--date must be complete Modes format: d.m.yyyy')
            sys.exit(1)
    return args


called_from_sphinx = True


if __name__ == '__main__':
    called_from_sphinx = False
    assert sys.version_info >= (3, 6)
    is_diff = sys.argv[1] == 'diff'
    is_select = sys.argv[1] == 'select'
    is_update = sys.argv[1] == 'update'
    is_validate = sys.argv[1] == 'validate'
    _args = getargs(sys.argv)
    verbose = _args.verbose
    if is_update and _args.object:
        if not _args.location:
            raise(ValueError('You specified the object id. You must also '
                             'specify the location.'))
        objectlist = expand_idnum(_args.object)
        newlocs = {nd.normalize_id(obj): _args.location for obj in objectlist}
        trace(2, 'Object(s) specified, newlocs= {}', newlocs)
    else:
        newlocs, newreasons = loadcsv()
    total_in_csvfile = len(newlocs)
    total_updated = total_written = 0
    total_failed = total_objects = 0  # validate only
    infile = open(_args.infile, encoding=_args.encoding)
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
