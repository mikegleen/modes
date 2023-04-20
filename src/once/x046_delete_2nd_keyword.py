# -*- coding: utf-8 -*-
"""
    For objects containing two keywords
"""
import argparse
import os.path
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

MEDIUMPATH = './Description/Material[Part="medium"]'


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_object(oldobj):
    """

    :param oldobj: the Object from the old file
    :return: True if the duplicate keyword element is removed, False otherwise
    """
    global object_number
    identification = oldobj.find('./Identification')
    if identification is None:
        print(f'No Identification: {object_number}')
        return False
    if oldobj.get('elementtype') != 'Original Artwork':
        return False
    medium = oldobj.find(MEDIUMPATH)
    if medium is None:
        print(f'No Medium: {object_number}')
        return False
    keywords = medium.findall('./Keyword')
    if len(keywords) < 2:
        return False
    lastkeyword = keywords[-1]
    if lastkeyword.text is None or len(lastkeyword.text.strip()) == 0:
        medium.remove(lastkeyword)
        return True
    return False


def main():
    global updatecount, writtencount, object_number
    declaration = f'<?xml version="1.0" encoding="{_args.encoding}"?>\n'
    outfile.write(bytes(declaration, encoding=_args.encoding))
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
        updated = one_object(oldobject)
        if updated:
            updatecount += 1
        writtencount += 1
        outfile.write(ET.tostring(oldobject, encoding=_args.encoding))
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
    parser.add_argument('-e', '--encoding', default='utf-8', help='''
        Set the output encoding. The default is "utf-8".
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
    updatecount = writtencount = 0
    object_number = ''
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
    basename = os.path.basename(sys.argv[0])
    print(f'{updatecount} object{"" if updatecount == 1 else "s"} updated.',
          file=sys.stderr)
    print(f'{writtencount} object{"" if writtencount == 1 else "s"} written.',
          file=sys.stderr)
    print(f'End {basename.split(".")[0]}', file=sys.stderr)

