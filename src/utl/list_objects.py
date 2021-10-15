"""
    Read a Modes XML file and return a list of the ObjectIdentity/Number text
    of each Object element. The list elements are tuples of:
        <normalized id>, <not normalized id>
"""

import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfgutil import Config
from utl.normalize import normalize_id


def list_objects(infile):
    """
    Extract the accession numbers from the Object elements in an XML file
    :param infile: filename or file object containing XML data
    :return: a list of tuples of (<normalized id>, <not normalized id>)
    """
    objectlevel = 0
    config = Config()  # get default values
    idnums = []
    for event, elem in ET.iterparse(infile, events=('start', 'end')):
        # print(event)
        if event == 'start':
            # print(elem.tag)
            if elem.tag == config.record_tag:  # default: Object
                objectlevel += 1
            continue
        # It's an "end" event.
        if elem.tag != config.record_tag:
            continue
        objectlevel -= 1
        if objectlevel:
            continue  # It's not a top level Object.
        data = []
        idelem = elem.find(config.record_id_xpath)
        idnum = idelem.text if idelem is not None else ''
        if idnum:
            idnums.append((normalize_id(idnum), idnum))

    idnums.sort()
    return idnums


if __name__ == "__main__":
    objects = list_objects(sys.argv[1])
    for _, obj in objects:
        print(obj)
