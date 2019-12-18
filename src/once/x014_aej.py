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

AEJSTR = r'([^(]*)\(?AEJ\s?(\d+)\)?(.*)'
aejpat = re.compile(AEJSTR)


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_elt(elt):
    global updatedcount
    ident = elt.find('./Identification')
    if ident is None:
        print(f'{object_number}: Identification not found')
        return False
    title = ident.find('./Title')
    if title is None:
        print(f'{object_number}: Title not found')
        return False
    if title.text is None:
        return False
    mt = aejpat.match(title.text)  # mt: match in title
    if mt is None:
        return False
    aejnum = mt.group(2)
    ref = elt.find('./References/Reference[@elementtype="AE Johnson Number"]')
    if ref is None:
        print(f'{object_number}: Reference not found')
        return False
    title.text = f'{mt.group(1)}{mt.group(3)}'
    ref.text = aejnum
    des = ident.find('./BriefDescription')
    if des is None:
        trace(1, "Brief Description missing from {}", object_number)
    else:
        mb = aejpat.match(des.text)  # mt: match in brief description
        if mb is not None:
            if aejnum != mb.group(2):
                print(f'{object_number}: title/description AEJ mismatch.')
            des.text = f'{mb.group(1)}{mb.group(3)}'
    updatedcount += 1
    return True


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
    updated = one_elt(oldobj)
    if updated or _args.all:
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
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects. The default is to only write updated objects.''')
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
    updatedcount = 0
    object_number = ''
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
    basename = os.path.basename(sys.argv[0])
    print(f'{updatedcount} objects updated.')
    print(f'End {basename.split(".")[0]}')

