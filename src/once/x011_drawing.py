# -*- coding: utf-8 -*-
"""
        For objects where the type of object is "drawing", remove the extraneous text
        "Drawing - " from the beginning of the BriefDescription element text.

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
    global updated
    etype = elt.get('elementtype')
    if etype is None or etype != 'Original Artwork':
        return
    ident = elt.find('./Identification')
    keyword = ident.find('./ObjectName[@elementtype="Type of Object"]/Keyword')
    if keyword is None or keyword.text != 'drawing':
        return
    des = ident.find('./BriefDescription')
    if des is None:
        trace(1, "Brief Description missing from {}", object_number)
        return
    m = re.match(r'(Drawing - )(.*)', des.text)
    if m:
        des.text = m.group(2)
        updated += 1
    return


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
    outfile.write(ET.tostring(oldobj, encoding=_args.encoding))


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
        For objects where the type of object is "drawing", remove the extraneous text
        "Drawing - " from the beginning of the BriefDescription element text.        
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-e', '--encoding', default='us-ascii', help='''
        Set the output encoding. The default is "us-ascii".
        ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    updated = 0
    object_number = ''
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
    basename = os.path.basename(sys.argv[0])
    print(f'{updated} objects updated.')
    print(f'End {basename.split(".")[0]}')

