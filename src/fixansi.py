# -*- coding: utf-8 -*-
"""
    Fix the problem that some characters in the XML file were incorrectly
    coded as windows-1252 instead of utf-8.
"""
import argparse
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_elt(elt):
    if elt.text is not None:
        text = elt.text
        text = text.replace('\u0091', '‘')  # 145
        text = text.replace('\u0092', '’')
        text = text.replace('\u0093', '“')
        text = text.replace('\u0094', '”')
        text = text.replace('\u0096', '–')
        elt.text = text
    # if not elt:
    #     return
    for e in elt:
        one_elt(e)


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
    outfile.write(b'<?xml version="1.0" encoding="utf-8"?>\n<Interchange>\n')
    for event, oldobject in ET.iterparse(infile):
        if oldobject.tag != 'Object':
            continue
        one_object(oldobject)
        oldobject.clear()
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Replace rogue ANSI characters (0x91 - 0x96) with the corresponding
        Unicode characters.
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
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    object_number = ''
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
