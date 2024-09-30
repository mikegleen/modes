# -*- coding: utf-8 -*-
"""
    Modify the XML structure.

    Rationalize the ``Description/Measurement/Part`` field.

    For cutting, ephemera, and letter elementtypes, the ``Description`` element
    group must have one ``Measurement/Part`` element with a text value of ``Image``.

"""
import argparse
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_elt(elt, objnum) -> bool:
    rtn = False
    etype = elt.get('elementtype')
    if etype is None:
        print(objnum, 'no elementtype')
        return rtn
    # print(objnum)
    des = elt.find('Description')
    if des is None:
        return rtn
    # aspects = des.findall('Aspect')
    # for aspect in aspects:
    #     keys = aspect.findall('Keyword')
    #     if len(keys) != 2:
    #         continue
    #     if keys[0].text == 'pages':
    #         keys[1].tag = 'Reading'
    #         rtn = True

    measlist = des.findall('Measurement')
    if len(measlist) == 3:
        return rtn
    if etype in ['cutting', 'ephemera']:
        meas = measlist[0]
        part = meas.find('Part')
        if part is None:
            part = ET.Element('Part')
            meas.insert(0, part)
        if part.text != 'image':
            part.text = 'image'
            rtn = True
    return rtn


def one_object(oldobj):
    """

    :param oldobj: the Object from the old file
    :return: None. The updated object is written to the output XML file.
    """
    global object_number, nwritten, nupdated
    numelt = oldobj.find('./ObjectIdentity/Number')
    if numelt is not None:
        object_number = numelt.text
    else:
        object_number = 'Missing'
    trace(2, '**** {}', object_number)
    rtn = one_elt(oldobj, object_number)
    if rtn:
        nupdated += 1
    if rtn or _args.all:
        nwritten += 1
        outfile.write(ET.tostring(oldobj, encoding=encoding))


def main():
    outfile.write(b'<?xml version="1.0" encoding="utf-8"?>\n<Interchange>\n')
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
        Modify the XML structure.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all records. ''')
    parser.add_argument('--ascii', action='store_true', help='''
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
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    object_number = ''
    nwritten = nupdated = 0
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    encoding = 'us-ascii' if _args.ascii else 'utf-8'
    main()
    print(f'End x055_part. {nupdated} objects updated. {nwritten} objects written.')

