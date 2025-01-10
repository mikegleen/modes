"""
    Subroutines called from update_from_csv.py to process the ``location`` command.
    These functions handle updating the normal and current locations. The script
    ``location.py`` provides additional functionality for location processing.
"""
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from collections.abc import Callable

from colorama import Fore

import utl.normalize as nd

NORMAL_LOCATION = 'normal location'
CURRENT_LOCATION = 'current location'
PREVIOUS_LOCATION = 'previous location'
ELEMENTTYPE = 'elementtype'


def update_normal_loc(ol: ET.Element, idnum: str, newtext: str, trace: Callable) -> bool:
    """
    :param ol: the ObjectLocation element
    :param idnum: the ObjectIdentity/Number text (we've tested that idnum is
    in newlocs)
    :param newtext: The new location value
    :param trace: function name
    :return: True if the object is updated, False otherwise
    """
    updated = False
    location = ol.find('./Location')
    if location.text is not None:
        oldtext = location.text.strip().upper()
    else:
        oldtext = None

    if oldtext != newtext:
        trace(2, '{}: Updated normal location: {} -> {}', idnum, oldtext, newtext)
        location.text = newtext
        updated = True
    else:
        trace(2, '{}: Normal location unchanged: {}', idnum, oldtext)
    return updated


def update_current_loc(elem: ET.Element, idnum: str, newtext: str,
                       newdate: str, newreason: str, trace: Callable) -> bool:
    """

    :param elem: the Object element
    :param idnum: the ObjectIdentity/Number text
    :param newtext: The new location value or "{{move_to_normal}}"
    :param newdate:
    :param newreason:
    :param trace: function name
    :return: True if the object is updated, False otherwise

    If --patch is set, change the date on the current location. Otherwise,
    change the current location into a previous location and insert a new
    current location element.

    We've called validate_locations() so there is no need to test return
    values from function calls.
    """

    # Find the current location
    ol = elem.find('./ObjectLocation[@elementtype="current location"]')

    locationelt = ol.find('./Location')
    datebeginelt = ol.find('./Date/DateBegin')
    if locationelt is None or datebeginelt is None:
        trace(1, '{}: Location or DateBegin subelt missing', idnum, color=Fore.RED)
        return False
    if newtext == '{{move_to_normal}}':
        nl = elem.find('./ObjectLocation[@elementtype="normal location"]')
        newlocationelt = nl.find('./Location')
        newlocationtext = newlocationelt.text.strip().upper()
    else:
        newlocationtext = newtext.upper()

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
        datebegin.text = newdate
        return True
    #
    # If a location has a valid date, make sure that it's older than the new
    # one we are creating.
    #
    try:
        new_loc_date, _ = nd.datefrommodes(newdate)
    except ValueError:
        trace(1, '{}: New date is badly formed: {}.', idnum, newdate,
              color=Fore.RED)
        return False
    oldlocdatetext = datebeginelt.text
    try:
        oldlocdate, _ = nd.datefrommodes(oldlocdatetext)
    except ValueError:
        oldlocdate = None
    if oldlocdate and new_loc_date < oldlocdate:
        trace(1, '{}: New date is older than existing date ({})',
              idnum, oldlocdatetext, color=Fore.RED)
        return False
    #
    # If the location hasn't changed, do nothing unless --force is set.
    #
    if oldlocation_upper == newlocationtext.upper():
        trace(1, 'Warning: Unchanged: {}: {}', idnum, locationelt.text, color=Fore.YELLOW)
        return False
    #
    # Create the new current location element.
    #
    newobjloc = ET.Element('ObjectLocation')
    newobjloc.set(ELEMENTTYPE, CURRENT_LOCATION)
    ET.SubElement(newobjloc, 'Location').text = newlocationtext
    locdate = ET.SubElement(newobjloc, 'Date')
    ET.SubElement(locdate, 'DateBegin').text = newdate
    if newreason:
        ET.SubElement(newobjloc, 'Reason').text = newreason
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
    oldateend.text = newdate
    ol.set(ELEMENTTYPE, PREVIOUS_LOCATION)
    #
    # insert the new current location before the old current location (which is
    # now a previous location.
    #
    elem.insert(clix - 1, newobjloc)

    trace(2, '{}: Updated current location: {} -> {}', idnum, locationelt.text,
          newlocationtext)
    return True
