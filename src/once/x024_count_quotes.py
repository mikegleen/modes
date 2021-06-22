# -*- coding: utf-8 -*-
"""
    Tally the first and last characters of the titles
"""
import argparse
from collections import defaultdict
import os.path
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_object(oldobj):
    """

    :param oldobj: the Object from the old file
    :return: None. The updated object is written to the output XML file.
    """
    global object_number
    title = oldobj.find('./Identification/Title')
    if title is not None:
        text = title.text
        if len(text) > 1:
            first = text[0]
            last = text[-1]
            if not first.isalnum():
                firsts[first] += 1
            if not last.isalnum():
                lasts[last] += 1
            if _args.verbose > 1 and (not first.isalnum() or not last.isalnum()):
                print(object_number, text)
            if text in titles:
                print(f'Duplicate title: {titles[text]}/{object_number}, {text[:80]}')
            titles[text] = object_number
    return False


def main():
    global updatecount, object_number
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
        oldobject.clear()


def getargs():
    parser = argparse.ArgumentParser(description='''
        For objects where the type of object is "drawing", remove the extraneous text
        "Drawing - " from the beginning of the BriefDescription element text.        
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    firsts = defaultdict(int)
    lasts = defaultdict(int)
    titles = dict()
    updatecount = 0
    object_number = ''
    _args = getargs()
    infile = open(_args.infile)
    main()
    firsts = {k: v for k, v in sorted(firsts.items(), key=lambda item: item[1],
                                      reverse=True)}
    lasts = {k: v for k, v in sorted(lasts.items(), key=lambda item: item[1],
                                     reverse=True)}
    print(f'{firsts=}')
    print(f'{lasts=}')
    basename = os.path.basename(sys.argv[0])
    print(f'End {basename.split(".")[0]}', file=sys.stderr)
