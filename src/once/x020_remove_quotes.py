# -*- coding: utf-8 -*-
"""
    Output selected Object elements based on the YAML configuration file.

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


def one_object(oldobj):
    """
    Remove leading numbering, like "23. text..."
    :param oldobj: the Object from the old file
    :return: None. The updated object is written to the output XML file.
    """
    global object_number
    title = oldobj.find('./Identification/Title')
    if title is not None:
        text = title.text
        # if (text.startswith('\N{LEFT SINGLE QUOTATION MARK}') and
        #    text.endswith('\N{RIGHT SINGLE QUOTATION MARK}')
        # if m := re.match(r"(\d+\.\s*)'([^']*)'$", text):
        if m := re.match(r"(\d+\.\s*)(.*)$", text):
            title.text = m.group(2)
            # trace(1, '{}: {} «{}»', object_number, text, title.text)
            trace(1, '{}: {}', object_number, text)
            return True
    return False


def one_object_fullstops(oldobj):
    """

    :param oldobj: the Object from the old file
    :return: None. The updated object is written to the output XML file.
    """
    global object_number
    title = oldobj.find('./Identification/Title')
    if title is not None:
        text = title.text
        # if (text.startswith('\N{LEFT SINGLE QUOTATION MARK}') and
        #    text.endswith('\N{RIGHT SINGLE QUOTATION MARK}')
        # if m := re.match(r"(\d+\.)?\s*'([^']*)'$", text):
        # if m := re.match(r"'(.*)'$", text):
        #     title.text = m.group(1)
        #     trace(1, '{}: {} «{}»', object_number, text, title.text)
        #     return True
        if m := re.match(r"(.*)([\w)\]”'’])\.$", text):
            title.text = text[:-1]
            # trace(1, '{}: {} «{}»', object_number, text, title.text)
            trace(1, '{}: {}', object_number, text)
            return True
    return False


def main():
    global updatecount, object_number
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
    updatecount = 0
    object_number = ''
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
    basename = os.path.basename(sys.argv[0])
    print(f'{updatecount} object{"" if updatecount == 1 else "s"} updated.',
          file=sys.stderr)
    print(f'End {basename.split(".")[0]}', file=sys.stderr)

