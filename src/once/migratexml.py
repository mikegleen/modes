# -*- coding: utf-8 -*-
"""
    Transpose the "fine art" template format XML to "Original Artwork" as
    defined by the hrm006.xml template.

    Additional editing:
    1. In 'Production/Method' and 'Description/Material/Part/Keyword' change
       'line' to 'pen and ink'.
    2. For objects with ID below JB600, change WxH to HxW

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
import re
import sys
import traceback
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

FINEART = 'fine art'
READING_PAT = re.compile(r'(\d+)[ xX]+(\d+)')  # W x H -> H x W
NUMBER_PAT = re.compile(r'JB\d{3}')
# Numbers lower than this will have their WxH reading flipped to HxW:
FLIP_LIMIT = 'JB600'


def trace(level, template, *args):
    if _args.verbose >= level:
        if level <= 1 and not _args.nored:
            fore, style = Fore.RED, Style.RESET_ALL
        else:
            fore, style = '', ''
        print(fore + template.format(*args) + style)
        if _args.walkback:
            try:
                raise IndexError
            except IndexError:
                traceback.print_stack()


def find2(oldobj, newobj, target):
    oldelt = oldobj.find(target)
    if oldelt is None:
        trace(1, '{}: find2 oldobj no find "{}"', object_number, target)
    newelt = newobj.find(target)
    if newelt is None:
        trace(1, '{}: find2 newobj no find "{}"', object_number, target)
    return oldelt, newelt


def copytext(oldobj, newobj, target):
    oldelt, newelt = find2(oldobj, newobj, target)
    if oldelt is not None:
        newelt.text = oldelt.text


def removeall(root, childtag):
    for child in root.findall('./' + childtag):
        root.remove(child)


def copymultiple(oldroot, newroot, childtag):
    """
    Remove all instances of childtag from newroot and copy all instances of
    oldroot's childtag. This only works in the case where childroot has only
    text and no other sub-elements.
    :param oldroot: the source element, child of Object
    :param newroot: the target element, child of Object
    :param childtag:
    :return:
    """
    removeall(newroot, childtag)
    for oldchild in oldroot.findall('./' + childtag):
        newchild = ET.Element(childtag)
        newchild.text = oldchild.text
        newroot.append(newchild)


def flip_reading(nm):
    """
    Change the Width x Height measurement to Height x Width.
    :param nm: The new "Measurement" element
    :return: None
    """
    reading = nm.find('./Reading')
    if reading is None:
        return
    if not reading.text:
        return
    m = READING_PAT.match(reading.text)
    if m:
        w = m.group(1)
        h = m.group(2)
        reading.text = f'{h}x{w}'
    else:
        trace(2,'{} cannot match dimension reading: {}', object_number,
              reading.text)


def update_conservation(oldobj, newobj):
    oldid, newid = find2(oldobj, newobj, './Conservation')
    copytext(oldid, newid, './SummaryText')
    copytext(oldid, newid, './Method')


def update_description(oldobj, newobj):
    old_description, new_description = find2(oldobj, newobj, './Description')
    copytext(old_description, new_description, './SummaryText')
    copytext(old_description, new_description, './Inscription/SummaryText')

    removeall(new_description, 'Material')
    for om in old_description.findall('./Material'):
        nm = ET.Element('Material')
        nm.append(ET.Element('Part'))
        copytext(om, nm, './Part')
        copymultiple(om, nm, 'Keyword')
        for nk in nm.findall('./Keyword'):
            if nk.text and nk.text.lower() == 'line':
                nk.text = 'pen and ink'
        new_description.append(nm)

    om = old_description.find('./Measurement[1]')
    nm = new_description.find('./Measurement[1]')
    copytext(om, nm, './Reading')
    if object_number < FLIP_LIMIT:
        flip_reading(nm)
    copytext(old_description, new_description, './Condition/Note')
    copytext(old_description, new_description, './Completeness/Note')


def update_identification(oldobj, newobj):
    oldid, newid = find2(oldobj, newobj, './Identification')
    copytext(oldid, newid, './Title')
    oldelt = oldid.find('./ObjectName[@elementtype="simple name"]/Keyword')
    newelt = newid.find('./ObjectName[@elementtype="Type of Object"]/Keyword')
    newelt.text = oldelt.text
    copytext(oldid, newid, './BriefDescription')


def update_object_identity(oldobj, newobj):
    copytext(oldobj, newobj, './ObjectIdentity/Number')


def update_object_location(oldobj, newobj):
    oldelt, newelt = find2(oldobj, newobj,
                           './ObjectLocation[@elementtype="current location"]')
    if oldelt is not None:
        copytext(oldelt, newelt, './Location')
        copytext(oldelt, newelt, './Date/DateBegin')

    oldelt, newelt = find2(oldobj, newobj,
                           './ObjectLocation[@elementtype="normal location"]')
    copytext(oldelt, newelt, './Location')


def update_production(oldobj, newobj):
    oldprod, newprod = find2(oldobj, newobj, './Production')
    copytext(oldprod, newprod, './SummaryText')
    copytext(oldprod, newprod, './Method')
    method = newprod.find('./Method')
    if method.text and method.text.lower() == 'line':
        method.text = 'pen and ink'

    oldelt, newelt = find2(oldprod, newprod, './Person')
    copytext(oldelt, newelt, './Role')
    copytext(oldelt, newelt, './PersonName')

    copytext(oldprod, newprod, './Date/DateBegin')
    copytext(oldprod, newprod, './Date/DateEnd')


def one_object(oldobj, newobj):
    """
    Populate the template with the data from the Modes XML file in the old
    format.

    :param oldobj: the Object from the old file
    :param newobj: the empty Object DOM structure
    :return: None. The new object is written to the output XML file.
    """
    global object_number
    numelt = oldobj.find('./ObjectIdentity/Number')
    if numelt is not None:
        object_number = numelt.text
    else:
        object_number = 'Missing'
    trace(2, '**** {}', object_number)
    if not NUMBER_PAT.match(object_number):
        trace(1, 'Warning, invalid object number: {}', object_number)
    update_object_identity(oldobj, newobj)
    update_object_location(oldobj, newobj)
    update_identification(oldobj, newobj)
    update_production(oldobj, newobj)
    update_description(oldobj, newobj)
    outfile.write(ET.tostring(newobj, encoding='us-ascii'))


def main():
    outfile.write(b'<?xml version="1.0" encoding="utf-8"?>\n<Interchange>\n')
    root = ET.parse(templatefile)
    object_template = root.find('Object')
    for event, oldobject in ET.iterparse(infile):
        if oldobject.tag != 'Object':
            continue
        if oldobject.attrib['elementtype'] != FINEART:
            continue
        newobject = copy.deepcopy(object_template)
        one_object(oldobject, newobject)
        oldobject.clear()
        newobject.clear()
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Create an XML file for loading into Modes.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes''')
    parser.add_argument('templatefile', help='''
        The new XML format template''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-r', '--nored', action='store_true', help='''
        Suppress the red highlighting of error messages. Useful when sending
        output to a file.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-w', '--walkback', action='store_true', help='''
        If set, print a stack walkback when a trace is done.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    object_number = ''
    _args = getargs()
    infile = open(_args.infile)
    templatefile = open(_args.templatefile)
    outfile = open(_args.outfile, 'wb')
    main()
