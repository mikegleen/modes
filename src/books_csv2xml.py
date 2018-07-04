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
from datetime import date
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(Fore.RED + template.format(*args) + Style.RESET_ALL)


def one_object(template, row):
    """
    Populate the template with the data from the CSV row.

    :param template: the empty Object DOM structure
    :param row: the CSV row
    :return: None. The object is written to the output XML file.
    """
    if not row['Serial']:
        trace(1, 'Skipping: {}', row)

    elt = template.find('./ObjectIdentity/Number')
    elt.text = row['Serial']

    elt = template.find('./Identification/Title')
    elt.text = row['Title']

    elt = template.find('./Production/Person[Role="author"]/PersonName')
    elt.text = row['Author']

    elt = template.find('./Production/Organisation[Role="publisher"]/OrganisationName')
    elt.text = row['Publisher']

    elt = template.find('./Production/Date[@elementtype="publication date"]')
    elt.text = row['Date']

    elt = template.find('./Notes')
    elt.text = row['Notes']

    elt = template.find('./ObjectLocation[@elementtype="current location"]/Location')
    elt.text = row['Location']

    elt = template.find('./ObjectLocation[@elementtype="current location"]/Date/DateBegin')
    elt.text = today

    elt = template.find('./ObjectLocation[@elementtype="normal location"]/Location')
    elt.text = row['Location']

    outfile.write(ET.tostring(template))


def one_ephemera_object(template, row):
    """
    Populate the template with the data from the CSV row.

    :param template: the empty Object DOM structure
    :param row: the CSV row
    :return: None. The object is written to the output XML file.
    """
    if not row['Serial']:
        trace(1, 'Skipping: {}', row)

    elt = template.find('./ObjectIdentity/Number')
    elt.text = row['Serial']

    elt = template.find('./Identification/Title')
    elt.text = row['Title']

    elt = template.find('./ObjectLocation[@elementtype="current location"]/Location')
    elt.text = row['Location']

    elt = template.find('./ObjectLocation[@elementtype="current location"]/Date/DateBegin')
    elt.text = today

    elt = template.find('./ObjectLocation[@elementtype="normal location"]/Location')
    elt.text = row['Location']

    outfile.write(ET.tostring(template))


def one_artwork_object(template, row):
    """
    This function is for the file 2018-06-04_artwork.csv containing fields:
        Serial,Title,Medium,Size,Location

    Populate the template with the data from the CSV row.

    :param template: the empty Object DOM structure
    :param row: the CSV row
    :return: None. The object is written to the output XML file.
    """
    if not row['Serial']:
        trace(1, 'Skipping: {}', row)

    elt = template.find('./ObjectIdentity/Number')
    elt.text = row['Serial']

    elt = template.find('./Identification/Title')
    elt.text = row['Title']

    elt = template.find('./ObjectLocation[@elementtype="current location"]/Location')
    elt.text = row['Location']

    elt = template.find('./ObjectLocation[@elementtype="current location"]/Date/DateBegin')
    elt.text = today

    elt = template.find('./ObjectLocation[@elementtype="normal location"]/Location')
    elt.text = row['Location']

    elt = template.find('./Description/Material[Part="medium"]/Keyword')
    elt.text = row['Medium']

    elt = template.find('./Production/Medium')
    elt.text = row['Medium']

    elt = template.find('./Description/Measurement[Part="Image"]/Reading')
    elt.text = row['Size']

    outfile.write(ET.tostring(template))


def main():
    outfile.write(b'<?xml version="1.0" encoding="utf-8"?>\n<Interchange>\n')
    root = ET.parse(templatefile)
    # print('root', root)
    # Assume that the template is really an Interchange file with empty
    # elements.
    object_template = root.find('Object')
    if not object_template:
        # Ok, so maybe it really is a template
        object_template = root.find('./template/Object')

    # print(object_template)
    reader = csv.DictReader(incsvfile)
    nrows = 0
    for row in reader:
        template = copy.deepcopy(object_template)
        if _args.ephemera:
            one_ephemera_object(template, row)
        elif _args.artwork:
            one_artwork_object(template, row)
        else:
            one_object(template, row)
        nrows += 1
    outfile.write(b'</Interchange>')
    print(f"{nrows} rows processed.\nEnd books_csv2xml.")


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
    parser.add_argument('--artwork', action='store_true', help='''
        Handle an artwork-format CSV file.''')
    parser.add_argument('--ephemera', action='store_true', help='''
        Handle an ephemera-format CSV file.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    today = date.isoformat(date.today())
    _args = getargs()
    incsvfile = open(_args.incsvfile, newline='', encoding='utf-8-sig')
    templatefile = open(_args.templatefile)
    outfile = open(_args.outfile, 'wb')
    main()
