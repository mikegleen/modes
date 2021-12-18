# -*- coding: utf-8 -*-
"""
    Update the Reproduction/Filename element to contain <id>.jpg
    Remove the attribute elementtype="Digital Image" from Reproduction
"""
import os.path
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

INPUTXML = 'prod_update/pretty/2021-12-12_location_pretty.xml'
OUPUTXML = 'prod_update/pretty/2021-12-16_reproduction_pretty.xml'


def one_object(oldobj):
    """
    :param oldobj: the Object from the old file
    :return: True if updated, False otherwise.
             The updated object will be written to the output XML file.
    """
    global updatecount, writtencount, object_number
    identification = oldobj.find('./Identification')
    if identification is None:
        print(f'No Identification: {object_number}')
        return False
    repro = oldobj.find('./Reproduction')
    if repro is None:
        print(f'No Reproduction: {object_number}')
        return False
    etype = repro.attrib.pop('elementtype', None)
    if etype:
        updatecount += 1
    filename = repro.find('./Filename')
    filename.text = f'{object_number}.jpg'
    writtencount += 1
    return True


def main():
    global updatecount, writtencount, object_number
    declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    outfile.write(bytes(declaration, encoding='UTF-8'))
    outfile.write(b'<Interchange>\n')
    objectlevel = 0
    for event, oldobject in ET.iterparse(infile, events=('start', 'end')):
        if event == 'start':
            if oldobject.tag == 'Object':
                objectlevel += 1
            continue
        # It's an "end" event.
        if oldobject.tag != 'Object':
            continue
        objectlevel -= 1
        if objectlevel:
            continue  # It's not a top level Object.
        idelem = oldobject.find('./ObjectIdentity/Number')
        object_number = idelem.text.upper() if idelem is not None else None
        one_object(oldobject)
        outfile.write(ET.tostring(oldobject, encoding='UTF-8'))
        oldobject.clear()
    outfile.write(b'</Interchange>')


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    updatecount = writtencount = 0
    object_number = ''
    infile = open(INPUTXML)
    outfile = open(OUPUTXML, 'wb')
    main()
    basename = os.path.basename(sys.argv[0])
    print(f'{updatecount} object{"" if updatecount == 1 else "s"} elementtypes removed.',
          file=sys.stderr)
    print(f'{writtencount} object{"" if writtencount == 1 else "s"} written.',
          file=sys.stderr)
    print(f'End {basename.split(".")[0]}', file=sys.stderr)

