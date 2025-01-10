"""
    Subroutines called from update_from_csv.py to process the ``location`` command.
    These functions handle updating the normal and current locations. The script
    ``location.py`` provides additional functionality for location processing.
"""
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from collections.abc import Callable

import utl.normalize as nd


def update_normal_location(ol: ET.Element, idnum: str, newtext: str, trace: Callable) -> bool:
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


