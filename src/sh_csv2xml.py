# -*- coding: utf-8 -*-
"""
    Create an XML file for loading into Modes.

    Input:
        1.  The CSV file created from the original Word document by saving the
            Word document as HTML and using sh_html2csv.py to create the CSV.
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


def one_object(template, row):
    elt = template.find('./ObjectLocation[@elementtype="current location"]/Location')
    elt.text = row['Location']
    elt = template.find('./ObjectLocation[@elementtype="normal location"]/Location')
    elt.text = row['Location']
    elt = template.find('./ObjectIdentity/Number')
    if row['Published']:
        if row['Published'] == 'unpublished':
            refs = template.find('./References[@elementtype="unpublished"]')
            ref = ET.Element('Reference', text='confirmed unpublished')
            refs.append(ref)
        else:
            ref = template.find('./References[@elementtype="magazine"]/Reference')
            title = ref.find('./Title')
            title.text = row['Published']
            date = ref.find('./Date')
            date.text = row['Date']

    if row['Serial']:
        elt.text = PREFIX + row['Serial']
        elt = template.find('./Identification/Title')
        elt.text = row['Title']
        outfile.write(ET.tostring(template))
    else:
        trace(1, 'Skipping: {}', row)


def main():
    outfile.write(b'<?xml version="1.0"?>\n<Interchange>\n')
    root = ET.parse(templatefile)
    object_template = root.find('Object')
    reader = csv.DictReader(incsvfile)
    for row in reader:
        template = copy.deepcopy(object_template)
        one_object(template, row)
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Create an XML file for loading into Modes.
        ''')
    parser.add_argument('incsvfile', help='''
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
    incsvfile = open(_args.incsvfile, newline='', encoding='utf-8-sig')
    templatefile = open(_args.templatefile)
    outfile = open(_args.outfile, 'wb')
    main()
