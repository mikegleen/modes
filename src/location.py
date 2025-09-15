# -*- coding: utf-8 -*-
"""
Utility for handling object location updating and checking.

There are three location types recorded in the XML database, the normal,
current, and previous locations. There may be multiple previous locations.

Exception: When updating a current location, a previous location element is
created (unless the ``--patch`` option is selected).
"""
import argparse
import time
from colorama import Fore, Style
from datetime import date
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
import utl.normalize as nd
from utl.cfgutil import expand_idnum
from utl.readers import row_dict_reader

NORMAL_LOCATION = 'normal location'
CURRENT_LOCATION = 'current location'
PREVIOUS_LOCATION = 'previous location'
ELEMENTTYPE = 'elementtype'
#
# FORCE_PATCH was implemented because the museum's policy briefly changed to
# never create previous locations. This has now been changed to create previous
# locations as normal.
FORCE_PATCH = False  # Set True to inhibit creating previous locations.
verbose = 1  # overwritten by _args.verbose; set here for unittest


def trace(level, template, *args, color=None):
    if verbose >= level:
        if color and not _args.nocolor:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def loadcsv():
    """
    Read the CSV file containing objectid -> location mappings, specified
    by the --mapfile argument.
    :return: the dictionary containing the mappings
    """
    rownum = 0
    rows = {}
    location_dict, reason_dict = {}, {}
    if _args.subp == 'validate':
        return location_dict, reason_dict
    loc_arg = _args.location
    # with codecs.open(_args.mapfile, encoding='utf-8-sig') as mapfile:
    reader = row_dict_reader(_args.mapfile, _args.verbose, _args.skiprows)
    for n in range(_args.skiprows):
        next(reader)
    for row in reader:
        rownum += 1
        if len(row) == 0:
            trace(2, 'Skipping empty row {}: {}', rownum, row)
            continue
        trace(3, 'row {}: {}', rownum, row, color=Fore.YELLOW)
        objid = row[_args.col_acc].strip().upper()
        if not objid:
            if ''.join(row):  # if there is anything else on the line
                trace(2, 'Skipping row with blank accession id: {}', row)
            continue
        objidlist = expand_idnum(objid)
        reason = ''
        if is_update:
            if _args.reason:
                reason = _args.reason
            elif _args.col_reason:
                try:
                    reason = row[_args.col_reason]
                except IndexError:
                    pass
        location = loc_arg if loc_arg else row[_args.col_loc].strip()
        for ob in objidlist:
            try:
                nobjid = nd.normalize_id(ob)
            except ValueError:
                continue  # normalize_id printed an error msg
            if not nobjid:
                print(f'Warning: Blank object ID row {rownum}: {row}')
                continue  # blank number
            if nobjid in location_dict:
                print(f'Error, row ignored: Duplicate object ID row {rownum}: '
                      f'{row}')
                continue
            location_dict[nobjid] = location
            reason_dict[nobjid] = reason
            rows[nobjid] = row
    return location_dict, reason_dict, rows


def handle_diff(idnum, elem):
    global total_diff
    # print('enter handle_diff')
    nidnum = nd.normalize_id(idnum)
    if nidnum not in newlocs:
        if _args.warn:
            trace(1, 'Not in CSV file: {}', idnum)
        return
    objlocs = elem.findall('./ObjectLocation')
    newdatetext = _args.date
    newdate, _ = nd.datefrommodes(newdatetext) if _args.date else None
    norm_ol = curr_ol = None
    for ol in objlocs:
        loc = ol.get(ELEMENTTYPE)
        if loc == NORMAL_LOCATION:
            norm_ol = ol
        elif loc == CURRENT_LOCATION:
            curr_ol = ol
        elif loc == PREVIOUS_LOCATION:
            pass
        else:
            trace(1, '{}: unrecognized location type.', idnum)
            continue
    if norm_ol is None:
        trace(1, '{}: Normal location missing.', idnum, color=Fore.RED)
        return
    if curr_ol is None:
        trace(1, '{}: Current location missing.', idnum, color=Fore.RED)
        return

    ol = curr_ol if _args.current else norm_ol

    location = ol.find('./Location')
    if location.text is not None:
        xml_loctext = location.text.strip().upper()
    else:
        xml_loctext = None
    # print(f'{xml_loctext=}')
    if _args.location:
        new_loctext = _args.location
    else:
        new_loctext = newlocs[nidnum]
        del newlocs[nidnum]
    # print(idnum, new_loctext, type(new_loctext))
    if not new_loctext:
        trace(1, '{}: New location unspecified', idnum)
        return
    trace(3, '{}: New location: {}', idnum, new_loctext)
    if xml_loctext == new_loctext:
        trace(2, '{}: Same: {}', idnum, xml_loctext)
        if _args.current:
            normloc = norm_ol.find('./Location')
            norm_loctext = normloc.text
            if norm_loctext is None:
                trace(1, '{}: empty normal location', idnum)
            else:
                norm_loctext = norm_loctext.upper()
                if norm_loctext != new_loctext:
                    trace(1, '{}: current {} != normal {}', idnum, new_loctext, norm_loctext)
    else:
        xmldateelt = ol.find('./Date/DateBegin')
        if xmldateelt is not None:
            xmldatetext = xmldateelt.text
            xmldate, _ = nd.datefrommodes(xmldatetext)
            if xmldate > newdate:
                trace(1, '{}: XML date ({}) is newer than CSV date ({})', idnum, xmldatetext,
                      newdatetext)
        trace(1, '{}: Different: XML: {}, CSV: {}', idnum, xml_loctext,
              new_loctext)
        total_diff += 1
        if _args.current:
            normloc = norm_ol.find('./Location')
            norm_loctext = normloc.text
            if norm_loctext == new_loctext:
                trace(1, '     {}: Moving to normal location ({})', idnum, new_loctext)
            elif norm_loctext == xml_loctext:
                trace(1, '     {}: Moving from normal location ({})', idnum, norm_loctext)


def validate_locations(idnum, elem, strict=True):
    """
    :param idnum:
    :param elem: The Object element
    :param strict: If False, allow gaps in the dates of the current and
    previous locations
    :return: True if valid, False otherwise
    """
    numnormal = numcurrent = 0
    objlocs = elem.findall('./ObjectLocation')
    #
    # locationdates will contain tuples of Date objects of (begindate, enddate)
    #
    locationdates = []
    for ol in objlocs:
        datebeginelt = ol.find('./Date/DateBegin')
        dateendelt = ol.find('./Date/DateEnd')
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
            if datebeginelt is None or datebeginelt.text is None:
                trace(1, 'E01 {}: No DateBegin for current location', idnum)
                return False
            try:
                datebegindate, _ = nd.datefrommodes(datebeginelt.text)
            except (ValueError, TypeError):
                trace(1,
                      'E02 {}: Invalid DateBegin for current location: "{}".',
                      idnum, datebeginelt.text)
                return False
            if dateendelt is not None and dateendelt.text:
                trace(1,
                      'E03 {}: DateEnd not allowed for current location: "{}".',
                      idnum, dateendelt.text)
                return False
            # None indicates this is current:
            locationdates.append((datebegindate, None))
        elif loctype == PREVIOUS_LOCATION:
            try:
                datebegindate, _ = nd.datefrommodes(datebeginelt.text)
            except (ValueError, TypeError):
                trace(1,
                      'E04 {}: Invalid DateBegin for previous location: "{}".',
                      idnum, datebeginelt.text)
                return False
            if dateendelt is None or not dateendelt.text:
                trace(1, 'E05 {}: Missing DateEnd for previous location.',
                      idnum)
                return False
            try:
                dateenddate, _ = nd.datefrommodes(dateendelt.text)
            except (ValueError, TypeError):
                trace(1,
                      'E06 {}: Invalid DateEnd for previous location: "{}".',
                      idnum, dateendelt.text)
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

    # Check that the youngest date is the current location and that there is
    # no overlap.
    locationdates.sort(key=lambda x: x[0], reverse=True)
    if locationdates[0][1] is not None:  # should not have an end date
        trace(1, 'E10 {}: current location is not the youngest.', idnum)
        return False
    prevbegin, prevend = locationdates[0]
    for nxtbegin, nxtend in locationdates[1:]:
        if nxtend < nxtbegin:
            trace(1, 'E11 {}: end date {} is younger than begin date {}.',
                  idnum, nxtbegin.isoformat(), nxtend.isoformat())
            return False
        if nxtend != prevbegin:
            if strict:
                trace(1, 'E12 {}: begin date "{}" not equal to previous end '
                         'date "{}".',
                      idnum, str(prevbegin), str(nxtend))
                return False
            elif nxtend > prevbegin:
                trace(1, 'E13 {}: Younger begin date "{}" overlaps with end '
                         'date. "{}".',
                      idnum, str(prevbegin), str(nxtend))
                return False
        prevbegin = nxtbegin
    return True


def update_normal_location(ol, idnum):
    """
    :param ol: the ObjectLocation element
    :param idnum: the ObjectIdentity/Number text (we've tested that idnum is
    in newlocs)
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
        trace(2, '{}: Updated normal location: {} -> {}', idnum, text, newtext)
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

    We've called validate_locations() so there is no need to test return
    values from function calls.

    """
    nidnum = nd.normalize_id(idnum)

    # Find the current location
    ol = elem.find('./ObjectLocation[@elementtype="current location"]')

    locationelt = ol.find('./Location')
    datebeginelt = ol.find('./Date/DateBegin')
    if locationelt is None or datebeginelt is None:
        trace(1, '{}: Location or DateBegin subelt missing', idnum, color=Fore.RED)
        return False
    if _args.move_to_normal:
        nl = elem.find('./ObjectLocation[@elementtype="normal location"]')
        newlocationelt = nl.find('./Location')
        newlocationtext = newlocationelt.text.strip().upper()
    else:
        newlocationtext = newlocs[nidnum] if newlocs[nidnum] else _args.location

    #
    # If the current location is empty, just insert the new location without
    # creating a previous location.
    #
    oldlocation_upper = locationelt.text.strip().upper()
    if not oldlocation_upper:
        trace(2, 'Inserting location into empty current location: {}: {}',
              idnum, newlocationtext)
        locationelt.text = newlocationtext
        datebegin = ol.find('./Date/DateBegin')
        datebegin.text = _args.date
        return True
    #
    # If a location has a valid date, make sure that it's older than the new
    # one we are creating.
    #
    oldlocdatetext = datebeginelt.text
    try:
        oldlocdate, _ = nd.datefrommodes(oldlocdatetext)
    except ValueError:
        oldlocdate = None
    if oldlocdate and new_loc_date < oldlocdate:
        if _args.force:
            trace(1, '{}: Warning: New date ({}) is older than existing date '
                     '({}) in current location',
                  idnum, new_loc_date, oldlocdatetext, color=Fore.YELLOW)
        else:
            trace(1, '{}: Fatal: New date is older than existing date ({})',
                  idnum, oldlocdatetext, color=Fore.RED)
            sys.exit(1)
    #
    # If the location hasn't changed, do nothing unless --force is set.
    #
    if oldlocation_upper == newlocationtext.upper():
        trace(2, 'Unchanged: {}: {}', idnum, locationelt.text)
        if _args.force:
            datebegin = ol.find('./Date/DateBegin')
            datebegin.text = _args.date
            return True
        else:
            return False

    must_patch = False
    if _args.patch or FORCE_PATCH:
        must_patch = True
    elif _args.col_patch is not None:
        try:
            patch_txt = newrows[nidnum][_args.col_patch]
            must_patch = bool(patch_txt.strip())  # True if populated
        except IndexError:
            pass  # False if the line is short

    if must_patch:
        datebeginelt.text = _args.date
        oldlocationtext = locationelt.text
        locationelt.text = newlocationtext
        reasonelt = ol.find('./Reason')
        reasontext = _args.reason if _args.reason else ''
        if newreasons[nidnum]:
            # The specific reason overrides the general one from the cmd line.
            reasontext = newreasons[nidnum]
        # Add the reason text "Patched" unless patching because of FORCEDPATCH
        if not FORCE_PATCH:
            if reasontext:
                reasontext += ' (Patched)'
            else:
                reasontext = 'Patched'
        if reasonelt is None and reasontext:
            reasonelt = ET.SubElement(ol, 'Reason')
        if reasontext:
            reasonelt.text = reasontext
        elif reasonelt is not None:
            # There may have been a previous reason but that is now obsolete.
            ol.remove(reasonelt)

        trace(2, '{}: Patched current location {} -> {}', idnum,
              oldlocationtext, newlocationtext)
        return True
    #
    # Create the new current location element.
    #
    newobjloc = ET.Element('ObjectLocation')
    newobjloc.set(ELEMENTTYPE, CURRENT_LOCATION)
    ET.SubElement(newobjloc, 'Location').text = newlocationtext
    locdate = ET.SubElement(newobjloc, 'Date')
    ET.SubElement(locdate, 'DateBegin').text = _args.date
    if newreasons[nidnum]:
        ET.SubElement(newobjloc, 'Reason').text = newreasons[nidnum]
    #
    # Find the current location's subelement index
    #
    subelts = list(elem)
    clix = 0  # index of the current location element
    for elt in subelts:
        clix += 1
        if (elt.tag == 'ObjectLocation'
                and elt.get(ELEMENTTYPE) == CURRENT_LOCATION):
            break
    #
    # Insert the DateEnd text in the existing current location and convert it
    # to a previous location
    #
    oldate = ol.find('./Date')
    oldateend = oldate.find('./DateEnd')
    if oldateend is None:
        oldateend = ET.SubElement(oldate, 'DateEnd')
    oldateend.text = _args.date
    ol.set(ELEMENTTYPE, PREVIOUS_LOCATION)
    #
    # insert the new current location before the old current location (which is
    # now a previous location.
    #
    elem.insert(clix - 1, newobjloc)

    trace(2, '{}: Updated current location: {} -> {}', idnum, locationelt.text,
          newlocationtext)
    return True


def update_previous_location(elem, idnum):
    print(f'Update of previous location not implemented. {elem=} {idnum=}')
    sys.exit(1)


def delete_previous(elem, idnum):
    subelts = elem.findall('./ObjectLocation')
    for elt in subelts:
        if elt.get(ELEMENTTYPE) == PREVIOUS_LOCATION:
            trace(2, 'Removing previous location from {}.', idnum)
            elem.remove(elt)


def loc_types(idnum, nidnum, args, rows):
    """
    Determine whether current and/or normal locations will be updated.
    :param idnum: Accession number from the CSV file for diagnostics
    :param nidnum: Normalized accession number from the CSV file to index
                   into global dictionary newrows
    :param args: The arguments returned by argparse or by a test driver.
    :param rows: The newrows global dictionary passed as a parameter to allow
                 unit testing
    :return: a 3-tuple of booleans for current, normal, and previous locations.
    """
    if args.col_loc_type is None:
        return args.current, args.normal, args.previous
    try:
        loc_type = rows[nidnum][args.col_loc_type].strip()
    except IndexError as e:
        raise Exception(f'Row with index {idnum} is too short; doesn‘t '
                        f'contain the location type.') from e
    if len(loc_type) < 1:
        return False, False, False
        # raise ValueError(f'{idnum} location type column empty.')
    current = normal = False
    # print(f'{loc_type=}')
    for c in loc_type:
        nc = c.upper()
        match nc:
            case 'C':
                current = True
            case 'N':
                normal = True
            case _:
                e = f'Illegal location type in CSV file for {idnum}: "{c}"'
                raise ValueError(e)
    return current, normal, None


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
        is_current, is_normal, is_previous = loc_types(idnum, nidnum, _args,
                                                       newrows)
        if is_normal:
            ol = elem.find('./ObjectLocation[@elementtype="normal location"]')
            updated = update_normal_location(ol, idnum)
        if is_current:
            updated |= update_current_location(elem, idnum)
        if is_previous:
            updated |= update_previous_location(elem, idnum)
        if _args.delete_previous:
            delete_previous(elem, idnum)
        del newlocs[nidnum]
    else:
        if _args.warn:
            trace(1, '{}: Not in CSV file', idnum)
    if nidnum in newlocs and not validate_locations(idnum, elem):
        trace(1, 'Failed post-update validation.')
        sys.exit(1)
    if outfile:
        outfile.write(ET.tostring(elem, encoding='utf-8'))
    if updated:
        if deltafile:
            deltafile.write(ET.tostring(elem, encoding='utf-8'))
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
    if _args.infile:
        trace(1, 'Input XML file: {}', _args.infile)
    if _args.mapfile:
        trace(1, 'Input data file: {}', _args.mapfile)
    if outfile:
        trace(1, 'Output XML file: {}', _args.outfile)
        outfile.write(b'<?xml version="1.0" encoding="utf-8"?><Interchange>\n')
    if deltafile:
        deltafile.write(b'<?xml version="1.0" encoding="utf-8"?><Interchange>\n')
        trace(1, 'Delta XML file: {}', _args.outfile)
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find('./ObjectIdentity/Number')
        idnum = idelem.text.upper() if idelem is not None else None
        trace(3, 'idnum: {}', idnum)
        # handle_diff() or handle_update() or handle_validate() :
        _args.func(idnum, elem)
        if _args.short:
            break
    if outfile:
        outfile.write(b'</Interchange>')
    if deltafile:
        deltafile.write(b'</Interchange>')
    if not _args.short:  # Skip warning if only processing one object.
        for nidnum in newlocs:
            trace(1, '{}: In CSV but not XML, ignored.', nd.denormalize_id(nidnum))


def add_arguments(parser, command):
    global is_update, is_diff, is_select, is_validate  # Needed for Sphinx
    # Define groups as None to avoid warnings from PyCharm.
    # map_group: --mapfile or --object
    # diff_group: --current or --normal
    diff_group = None  # only if diff command
    # patch_group: --col_patch or --patch
    patch_group = None
    if called_from_sphinx:
        is_update = command == 'update'
        is_diff = command == 'diff'
        is_select = command == 'select'
        is_validate = command == 'validate'
    parser.add_argument('-i', '--infile', required=True, help='''
        The XML file saved from Modes.''')
    if is_update:
        parser.add_argument('-o', '--outfile', help='''
            The output XML file containing all objects.''')
        parser.add_argument('--deltafile', help='''
            The XML file to contain updated objects.''')
    if is_select:
        parser.add_argument('-o', '--outfile', required=True, help='''
            The output XML file containing all objects.''')
    if is_update or is_diff:
        parser.add_argument('--col_acc', type=str, default='Serial', help='''
        The heading of the column containing the accession number of the
        object to be updated. The default is "Serial".
        ''')
        defloc = nd.if_not_sphinx(''' The default is Location.''',
                                  called_from_sphinx)
        parser.add_argument('--col_loc', type=str, default='Location',
                            help=nd.sphinxify('''
        The heading of the column containing the new location of the
        object to be updated. See the --location
        option which sets the default location for all objects being updated if
        the cell in the CSV file is not populated.''' + defloc, called_from_sphinx))
    if is_update:
        parser.add_argument('--col_loc_type', help=nd.sphinxify('''
        Set this column in the CSV file to ``c``, ``n``, or ``cn`` indicating
        that the current, normal, or both, respectively, should be updated.
        If this is set, do not set the -c or -n or -p argument.
        ''', called_from_sphinx))
        patch_group = parser.add_mutually_exclusive_group()
        patch_group.add_argument('--col_patch', help=nd.sphinxify('''
        Indicate that this column should contain
        “``patch``”, possibly abbreviated to “``p``”, or be empty. This is
        equivalent for this row to setting the --patch command-line option
        which applies to all of the rows in the CSV file. The column can be a
        number or a spreadsheet-style letter.''', called_from_sphinx))
        parser.add_argument('--col_reason', help=nd.sphinxify('''
            The zero-based column containing text to be inserted as the
            reason for the move to the new current location for the object
            named in the row. If this field is specified and --reason is also specified,
            the  --reason value will be used if this field is empty. The column can be a
            number or a spreadsheet-style letter.
            ''', called_from_sphinx))
        parser.add_argument('-c', '--current', action='store_true',
                            help=nd.sphinxify('''
        Update the current location and change the old current location to a
        previous location. You may also specify ``-n`` to update the normal
        location. See the descrption of ``-n`` and ``-p`` Do not specify
        this and --col_loc_type.''',
                                              called_from_sphinx))
    if is_diff:
        # diff_group: --current or --normal
        diff_group = parser.add_mutually_exclusive_group(required=True)
        diff_group.add_argument('-c', '--current', action='store_true',
                                help='''
        Compare the location in the CSV file to the current location in the
        XML file.''')
        parser.add_argument('-d', '--date', default=None,
                            help='''
            If specified, check that the current location DateBegin is before this date.
            ''')
    if is_update:
        parser.add_argument('-d', '--date', default=nd.modesdate(date.today()),
                            help='''
            When updating the current location, use this date as the DateEnd
            value for the new previous location and the DateBegin
            value for the new current location. The default is
            today's date in Modes format (d.m.yyyy).
            ''')
        parser.add_argument('--datebegin', help=nd.sphinxify('''
        When specifying the --previous option, use this string as the date to
        store in the new previous ObjectLocation
        date. The format must be in Modes format (d.m.yyyy).
        ''', called_from_sphinx))
        parser.add_argument('--dateend', default=nd.modesdate(date.today()),
                            help=nd.sphinxify('''
        When specifying the --previous option, use this string as the date to
        store in the new previous ObjectLocation
        date. The format must be in Modes format (d.m.yyyy).
        ''', called_from_sphinx))
        parser.add_argument('--delete_previous', action='store_true', help='''
        Only output the most recent current location element for each object,
        deleting all previous locations.
        ''')
    parser.add_argument('--encoding', default='utf-8', help='''
        Set the input encoding. Default is utf-8. Output is always utf-8.
        ''')
    if is_update:
        parser.add_argument('-f', '--force', action='store_true', help='''
        Write the object to the output file even if it hasn't been updated.
        This only
        applies to objects whose ID appears in the CSV file. -a implies -f.
        
        An illegal accession number format will be skipped instead of causing
        a fatal error.
        
        If a new date to be applied to a current location is older than the
        existing date, the date will be applied instead of causing a fatal error.
        ''')
    if is_update or is_diff or is_select:
        map_group = parser.add_mutually_exclusive_group(required=True)
        map_group.add_argument('-j', '--object', help=nd.sphinxify('''
        Specify a single object to be processed. If specified, do not specify
        --mapfile, the CSV file containing object numbers and locations.
        The object specified can be a range of objects. You
        must also specify --location.
        ''', called_from_sphinx))
        parser.add_argument('-l', '--location', help=nd.sphinxify('''
        Set the location for all of the objects in the CSV file. In this 
        case the CSV file only needs a single column containing the 
        accession number. If --col_loc is also specified, this location will
        be used if that cell is not populated.
        ''', called_from_sphinx))
        map_group.add_argument('-m', '--mapfile', help=nd.sphinxify('''
            The CSV file mapping the object number to its new location. By
            default, the accession number is in the column with header "Serial" but 
            this can be changed by the --col_acc option. The new location is by
            default in the column with header "Location" but can be changed by the
            --col_loc option. This  argument is ignored if --object is
            specified.
            ''', called_from_sphinx))
    parser.add_argument('--nocolor', action='store_true', help='''
                        Inhibit colorizing the output which makes reading redirected output easier''')
    if is_update:
        parser.add_argument('-q', '--move_to_normal', action='store_true',
                            help=nd.sphinxify('''
            Implies -c. Updates the current location. Do not specify this
            and --col_loc_type. If you select --move_to_normal 
            you may not select --normal or --previous''', called_from_sphinx))
        parser.add_argument('-n', '--normal', action='store_true',
                            help=nd.sphinxify('''
            Update the normal location. You may also specify ``-c`` to update
            the current location.  See the description for ``-c`` and ``-p``.
            Do not specify this and --col_loc_type.''', called_from_sphinx))
    if is_diff:
        diff_group.add_argument('-n', '--normal', action='store_true', help='''
        Compare the location in the CSV file to the normal location in the
        XML file.''')
        parser.add_argument('--old', action='store_true', help='''
            The column selected is the "old" location, the one we are moving
            the object from. Warn if the value in the CSV file does not match
            the value in the XML file. The default is to warn if the value in
            the CSV file does match the value in the XML file which is not
            expected as the purpose is to update that value.
            ''')
    if is_update:
        patch_group.add_argument('--patch', action='store_true', help='''
        Update the specified current location in place without creating
        history. This is always the behavior for normal locations but not for
        current or previous.
        ''')
        parser.add_argument('-p', '--previous', action='store_true',
                            help=nd.sphinxify('''
        Add a previous location. This location's start and end dates must 
        not overlap with an existing current or previous location's date(s). 
        If "-p" is selected, do not select "-n" or "-c". If "-p" is specified,
        you must specify --datebegin and --dateend. Do not specify
        this and --col_loc_type.
        ''', called_from_sphinx))
        parser.add_argument('-r', '--reason', default='',
                                  help=nd.sphinxify('''
        Insert this text as the reason for the move to the new current location
        for all of the objects updated. See also --col_reason.
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
    Specify one of the functions defined by the positional parameters. For
    further details, specify ``-h`` after the function name.
        ''', called_from_sphinx))
    subparsers = parser.add_subparsers(dest='subp')
    diff_parser = subparsers.add_parser('diff', description=nd.sphinxify('''
    Compare the location of the object in the mapfile as
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
        if args.col_loc_type:
            if args.current or args.normal:
                trace(0, 'You may not specify both --col_loc_type and -c or -n.')
                sys.exit(1)
        if args.move_to_normal:
            if args.normal or args.previous:
                trace(0, 'If you select --move_to_normal you may not select '
                      '--normal or --previous.', color=Fore.RED)
                sys.exit(1)
            args.current = True
        if not nd.vdate(args.date):
            print('--date must be complete Modes format: d.m.yyyy')
            sys.exit(1)
    if (is_update or is_select) and args.infile == args.outfile:
        trace(0, 'Fatal error: Input and output files must be different.',
              color=Fore.RED)
        sys.exit(1)
    return args


called_from_sphinx = True


if __name__ == '__main__':
    called_from_sphinx = False
    assert sys.version_info >= (3, 6)
    t1 = time.perf_counter()
    if len(sys.argv) <= 2:
        sys.argv.append('-h')
    is_diff = sys.argv[1] == 'diff'
    is_select = sys.argv[1] == 'select'
    is_update = sys.argv[1] == 'update'
    is_validate = sys.argv[1] == 'validate'
    _args = getargs(sys.argv)
    verbose = _args.verbose
    if is_update:
        new_loc_date, _ = nd.datefrommodes(_args.date)
    trace(1, 'Begin location {}.', _args.subp,
          color=Fore.GREEN)
    if is_update and _args.object:
        if not _args.location and not _args.move_to_normal:
            trace(0, 'You specified the object id. You must also '
                     'specify the location.', color=Fore.RED)
        objectlist = expand_idnum(_args.object)
        newlocs = {nd.normalize_id(obj): _args.location for obj in objectlist}
        newreasons = {nd.normalize_id(obj): _args.reason for obj in objectlist}
        newrows = None  # will be ignored if -j is set
        trace(2, 'Object(s) specified, newlocs= {}', newlocs)
    elif is_validate:
        newlocs = {}
    else:
        newlocs, newreasons, newrows = loadcsv()
    total_in_csvfile = len(newlocs)
    total_updated = total_written = total_diff = 0
    total_failed = total_objects = 0  # validate only
    infile = open(_args.infile, encoding=_args.encoding)
    outfile = deltafile = None
    if _args.outfile:
        outfile = open(_args.outfile, 'wb')
        trace(1, 'Creating output file: {}', _args.outfile)
    if _args.deltafile:
        deltafile = open(_args.deltafile, 'wb')
        trace(1, 'Creating delta file: {}', _args.deltafile)
    main()
    if is_update:
        print(f'Total Updated: {total_updated}/{total_in_csvfile}\n'
              f'Total Written: {total_written}')
    elif is_validate:
        print(f'Total failed: {total_failed}/{total_objects}.')
    elif is_diff:
        print(f'Total different: {total_diff}/{total_in_csvfile}')
    elapsed = time.perf_counter() - t1
    trace(1, 'End location {}.  Elapsed: {:5.2f} seconds.', _args.subp,
          elapsed, color=Fore.GREEN)
