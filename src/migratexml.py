# -*- coding: utf-8 -*-
"""
    Transpose the "fine art" template format XML to "Original Artwork" as
    defined by the hrm006.xml template.

    Input:
        1.  The XML file created by Modes support using the "fine art" template
        2.  The template file for creating the DOM object that will be
            populated by this program
    Output:
            The XML file to import to Modes.
"""
import argparse
from colorama import Fore, Style
import copy
import csv
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

PREFIX = 'SH'


def trace(level, template, *args):
    if _args.verbose >= level:
        print(Fore.RED + template.format(*args) + Style.RESET_ALL)


def find2(oldobj, newobj, target):
    oldelt = oldobj.find(target)
    newelt = newobj.find(target)
    return oldelt, newelt


def updatetext(oldobj, newobj, target):
    oldelt, newelt = find2(oldobj, newobj, target)
    newelt.text = oldelt.text


def update_object_identity(oldobj, newobj):
    updatetext(oldobj, newobj, './ObjectIdentity/Number')


def update_object_location(oldobj, newobj):
    oldelt, newelt = find2(oldobj, newobj,
                           './ObjectLocation[@elementtype="current location"]')
    updatetext(oldelt, newelt, './Location')
    updatetext(oldelt, newelt, './Date/DateBegin')

    oldelt, newelt = find2(oldobj, newobj,
                           './ObjectLocation[@elementtype="normal location"]')
    updatetext(oldelt, newelt, './Location')


def update_identification(oldobj, newobj):
    oldid, newid = find2(oldobj, newobj, './Identification')
    updatetext(oldid, newid, './Title')
    oldelt = oldid.find('./ObjectName[@elementtype="simple name"/Keyword')
    newelt = newid.find('./ObjectName[@elementtype="Type of Object"/Keyword')
    newelt.text = oldelt.text
    updatetext(oldid, newid, './BriefDescription')


def one_object(oldobj, newobj):
    """
    Populate the template with the data from the CSV row.

    :param oldobj: the Object from the old file
    :param newobj: the empty Object DOM structure
    :return: None. The new object is written to the output XML file.
    """
    update_object_identity(oldobj, newobj)
    update_object_location(oldobj, newobj)

    if not row['Serial']:
        trace(1, 'Skipping: {}', row)

    elt = newobj.find('./ObjectLocation[@elementtype="current location"]/Location')
    elt.text = row['Location']
    elt = newobj.find('./ObjectLocation[@elementtype="normal location"]/Location')
    elt.text = row['Location']

    elt = newobj.find('./ObjectIdentity/Number')
    elt.text = PREFIX + row['Serial']

    elt = newobj.find('./Identification/Title')
    elt.text = row['Title']

    if row['Published']:
        elt = newobj.find('./References/Reference[@elementtype="First Published In"]')
        title = elt.find('Title')
        title.text = row['Published']
        date = elt.find('./Date')
        date.text = row['Date']
    outfile.write(ET.tostring(newobj))


def main():
    outfile.write(b'<?xml version="1.0" encoding="utf-8"?>\n<Interchange>\n')
    root = ET.parse(templatefile)
    object_template = root.find('Object')
    for event, oldobject in ET.iterparse(infile):
        if oldobject.tag != 'Object':
            continue
        newobject = copy.deepcopy(object_template)
        one_object(oldobject, newobject)
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Create an XML file for loading into Modes.
        ''')
    parser.add_argument('infile', help='''
        The CSV file containing the data from the Word document''')
    parser.add_argument('templatefile', help='''
        The XML format template''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    _args = getargs()
    infile = open(_args.infile)
    templatefile = open(_args.templatefile)
    outfile = open(_args.outfile, 'wb')
    main()
