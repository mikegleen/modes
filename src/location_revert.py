# -*- coding: utf-8 -*-
"""
Utility for fixing an error in the location.

1. Delete the current location.
2. Change the previous location to a current location, deleting the DateEnd
   element.
3. Optionally changing the normal location.


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
    location_dict = {}
    loc_arg = _args.location
    need_heading = bool(_args.heading)
    with codecs.open(_args.mapfile, 'r', 'utf-8-sig') as mapfile:
        reader = csv.reader(mapfile)
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
            if not objid and ''.join(row):
                trace(2, 'Skipping row with blank object id: {}', row)
                continue
            objidlist = expand_idnum(objid)
            for ob in objidlist:
                nobjid = nd.normalize_id(ob)
                if not nobjid:
                    print(f'Warning: Blank object ID row {rownum}: {row}')
                    continue  # blank number
                if nobjid in location_dict:
                    print(f'Fatal error: Duplicate object ID row {rownum}: {row}.')
                    sys.exit(1)
                location_dict[nobjid] = loc_arg if loc_arg else row[_args.col_loc].strip()
    return location_dict


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
    ET.SubElement(newobjloc, 'Reason').text = _args.reason

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
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('-o', '--outfile', required=True, help='''
        The output XML file.''')
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
    parser.add_argument('-c', '--current', action='store_true', help='''
    Update the current location and change the old current location to a
    previous location. See the descrption of "n" and "p". ''')
    parser.add_argument('--encoding', default='utf-8', help='''
        Set the input encoding. Default is utf-8. Output is always utf-8.
        ''')
    parser.add_argument('--heading', help=nd.sphinxify('''
        The first row of the map file contains a column title which must match the
        parameter (case insensitive) in the column designated for the location.
        If a --location argument is specified, the first row is skipped and the
        value, which nevertheless must be specified, is ignored. 
        ''', called_from_sphinx))
    parser.add_argument('-m', '--mapfile', help=nd.sphinxify('''
        The CSV file mapping the object number to its new location. By
        default, the accession number is in the first column (column 0) but 
        this can be changed by the --col_acc option. The new location is by
        default in the second column (column 1) but can be changed by the
        --col_loc option. This  argument is ignored if --object is specified.
        ''', called_from_sphinx))
    if is_update or is_diff:
        parser.add_argument('-n', '--normal', help='''
        The new normal location''')
    parser.add_argument('-j', '--object', help=nd.sphinxify('''
    Specify a single object to be processed. If specified, do not specify
    the CSV file containing object numbers and locations (--mapfile).
    ''', called_from_sphinx))
    parser.add_argument('-r', '--reason', default='', help='''
        Insert this text as the reason for the move to the new current location.
        ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process a single object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
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
    With no options, check that the location in the object specified by --col_loc
    is the same as the location specified by -c or -n option in the XML file.
    ''', called_from_sphinx))
    select_parser = subparsers.add_parser('select', description='''
    Select the objects named in the CSV file specified by -m and write them to the
    output without modification. 
    ''')
    update_parser = subparsers.add_parser('update', description='''
    Update the XML file from the location in the CSV file specified by -m.
    ''')
    validate_parser = subparsers.add_parser('validate', description='''
    Run the validate_locations function against the input file. This validates all
    locations and ignores the -c, -n, and -p options. Check that dates exist
    and do not overlap.
    ''')
    diff_parser.set_defaults(func=handle_diff)
    select_parser.set_defaults(func=handle_select)
    update_parser.set_defaults(func=handle_update)
    validate_parser.set_defaults(func=handle_validate)
    add_arguments(diff_parser, 'diff')
    add_arguments(select_parser, 'select')
    add_arguments(update_parser, 'update')
    add_arguments(validate_parser, 'update')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if is_diff or is_update:
        # Set a fake value for the new location column as it will be taken from
        #  the --location value instead of a column in the CSV file.
        if args.location:
            args.col_loc = None
    if is_update:
        nloctypes = int(args.current) + int(args.previous) + int(args.normal)
        if nloctypes != 1:
            print('Exactly one of -c or -p must be specified.')
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
        newlocs = loadcsv()
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
