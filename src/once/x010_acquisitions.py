# -*- coding: utf-8 -*-
"""
    Reorganize the Acquisitions/Person element. Currently it could be
    Object elementtype="Original Artwork":
        <Person>Denis Brinsmead
            <Role>acquired from</Role>
            <PersonName/>
            <Address/>
            <Phone/>
        </Person>
    or
    Object elementtype="books":
        <Person elementtype="Acquired from">Denis Brinsmead</Person>

Convert these to:
        <Person>
            <Role>acquired from</Role>
            <PersonName>Denis Brinsmead</PersonName>
            <Address/>  <-- only if it's populated
        </Person>
"""
import argparse
import os.path
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_elt(elt):
    acq = elt.find('./Acquisition')
    acq.attrib = {}  # get rid of elementtype="Acquisition Method" attributes
    person = acq.find('./Person')
    role = person.find('./Role')
    person_name = person.find('./PersonName')
    address = person.find('./Address')
    person_text = person.text.strip() if person.text else ''
    person_name_text = (person_name.text if person_name is not None and
                        person_name.text is not None else '')

    person.clear()

    if role is not None and role.text:
        ET.SubElement(person, 'Role').text = role.text
    else:
        ET.SubElement(person, 'Role').text = 'acquired from'
    if person_text:
        name = person_text
        # print(f'person_text: "{person_text}"')
    else:
        # name = person_name.text if person_name is not None else ''
        name = person_name_text.strip()
        # print(name)
    ET.SubElement(person, 'PersonName').text = name
    if address is not None and address.text:
        ET.SubElement(person, 'Address').text = address.text


def one_object(oldobj):
    """

    :param oldobj: the Object from the old file
    :return: None. The updated object is written to the output XML file.
    """
    global object_number
    numelt = oldobj.find('./ObjectIdentity/Number')
    if numelt is not None:
        object_number = numelt.text
    else:
        object_number = 'Missing'
    trace(2, '**** {}', object_number)
    one_elt(oldobj)
    encoding = 'us-ascii' if _args.ascii else 'utf-8'
    outfile.write(ET.tostring(oldobj, encoding=encoding))


def main():
    declaration = f'<?xml version="1.0" encoding="{_args.encoding}"?>\n'
    outfile.write(bytes(declaration, encoding=_args.encoding))
    outfile.write(b'<Interchange>\n')
    for event, oldobject in ET.iterparse(infile):
        if oldobject.tag != 'Object':
            continue
        one_object(oldobject)
        oldobject.clear()
        if _args.short:
            break
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Modify the XML structure. Reorganize the Acquisitions/Person element.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--ascii', action='store_true', help='''
        Create the output XML file using the us-ascii encoding rather than
        utf-8. This means that non-ascii characters will be encoded with
        sequences such as "&#8220" meaning the left double quote character.
        ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    args.encoding = 'us-ascii' if args.ascii else 'utf-8'
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 7)
    object_number = ''
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
    basename = os.path.basename(sys.argv[0])
    print(f'End {basename.split(".")[0]}')

