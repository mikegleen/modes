# -*- coding: utf-8 -*-
"""
    Book: # of pages
    Remove the Description/Aspect element and replace it with a
    Description/Measurement measurement

"""
import argparse
import os.path
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_elt(elt):
    des = elt.find('./Description')
    aspect = des.find('./Aspect')
    if aspect is None:
        return
    des.remove(aspect)
    newmeas = ET.Element('Measurement')
    ET.SubElement(newmeas, 'Part').text = 'pages'
    ET.SubElement(newmeas, 'Dimension').text = 'count'
    ET.SubElement(newmeas, 'Reading')
    nelt = 0
    nmeas = 0  # index of the last Measurement element
    for subelt in des:
        nelt += 1
        if subelt.tag == 'Measurement':
            nmeas = nelt
    # Insert the new Measurement subelement after the last existing one
    des.insert(nmeas, newmeas)

    # Convert the accession number format from LDHRM/2018/1 to LDHRM.2018.1
    if object_number.startswith('LDHRM'):
        m = re.match(r'LDHRM/(\d{4})/(\d+)', object_number)
        if not m:
            trace(0, 'object number starting LDHRM fails match: {}',
                  object_number)
            return
        newnumber = f'LDHRM.{m.group(1)}.{m.group(2)}'
        numelt = elt.find('./ObjectIdentity/Number')
        numelt.text = newnumber


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
        Modify the XML structure. Remove the Description/Aspect element and
        replace it with a Description/Measurement element. Also convert
        object numbers from the form "LDHRM/2018/1" to "LDHRM.2018.2".
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
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    object_number = ''
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
    basename = os.path.basename(sys.argv[0])
    print(f'End {basename.split(".")[0]}')

