# -*- coding: utf-8 -*-
"""
    Update SH objects with empty current location start date.
"""
import argparse
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_elt(elt):
    if not object_number.startswith('SH'):
        return False
    currloc = elt.find('./ObjectLocation[@elementtype="current location"]/Location')
    begdate = elt.find('./ObjectLocation[@elementtype="current location"]/Date/DateBegin')
    if begdate is None:
        trace(1,'{}: Missing DateBegin element.', object_number)
        return False
    updated = False
    if begdate.text is None:
        if currloc.text == 'NMOC':
            begdate.text = '20.3.2019'
        else:
            begdate.text = '13.4.2015'
        updated = True
    return updated


def one_object(oldobj):
    """

    :param oldobj: the Object from the old file
    :return: None. The updated object is written to the output XML file.
    """
    global object_number, total_updated
    numelt = oldobj.find('./ObjectIdentity/Number')
    if numelt is not None:
        object_number = numelt.text
    else:
        object_number = 'Missing'
    trace(2, '**** {}', object_number)
    updated = one_elt(oldobj)
    if updated:
        outfile.write(ET.tostring(oldobj, encoding='us-ascii'))
        total_updated += 1


def main():
    outfile.write(b'<?xml version="1.0" encoding="utf-8"?>\n<Interchange>\n')
    for event, oldobject in ET.iterparse(infile):
        if oldobject.tag != 'Object':
            continue
        one_object(oldobject)
        oldobject.clear()
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Modify the XML structure.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    object_number = ''
    total_updated = 0
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
    print(f'Total updated: {total_updated}.')

