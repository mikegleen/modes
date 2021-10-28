# -*- coding: utf-8 -*-
"""
    Modify the XML structure. If Production/Date/DateBegin == unknown:
    1. Change the <DateBegin> text to ""
    2. If the input CSV has a decade, enter <DateBegin>, <DateEnd> and set
       <Accuracy>circa</Accuracy>
    3. If CSV file has an estimated date "ca...." as circa, add an
       <Accuracy>circa</Accuracy> to the <Date>


"""
import codecs
import csv
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

CSVFILENAME = 'data/fromgeoffrey/2021-10-19_dates.csv'
INPUTXML = 'prod_update/pretty/2021-10-20_edited_pretty.xml'
OUTPUTXML = 'prod_update/pretty/2021-10-27_unknown_date_pretty.xml'

TRACE = 1


def trace(level, template, *args):
    if TRACE >= level:
        print(template.format(*args))


def one_elt(elt):
    date = elt.find('./Production/Date')
    datebegin = date.find('./DateBegin')
    if datebegin is None:
        return
    if datebegin.text == 'unknown':
        if object_number not in dates:
            datebegin.text = ''
            return
        ca_year, decade = dates[object_number]
        m = re.match(r'ca\.\s?(\d{4})', ca_year)
        if m:
            year = m.group(1)
        else:
            year = None
        if year and decade:
            print('********* Year and decade', object_number)  # bad data
            return
        if year:
            datebegin.text = year
            accuracy = ET.SubElement(date, 'Accuracy')
            accuracy.text = 'circa'
            return
        if decade:
            datebegin.text = decade[:4]  # 1910s -> 1910
            dateend = date.find('DateEnd')
            if dateend is None:
                dateend = ET.SubElement(date, 'DateEnd')  # assume none exist yet
            dateend.text = decade[:3] + '9'  # 1910s -> 1919
            accuracy = ET.SubElement(date, 'Accuracy')
            accuracy.text = 'decade'
            return
        print('No year or decade', object_number)  # internal error
        return


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
    encoding = 'utf-8'
    outfile.write(ET.tostring(oldobj, encoding=encoding))


def main():
    for row in csvreader:
        # print(row)
        if row['Year'] or row['Decade']:
            dates[row['Serial']] = (row['Year'], row['Decade'])
    outfile.write(b'<?xml version="1.0" encoding="UTF-8"?>\n<Interchange>\n')
    for event, oldobject in ET.iterparse(infile):
        if oldobject.tag != 'Object':
            continue
        one_object(oldobject)
        oldobject.clear()
    outfile.write(b'</Interchange>')


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    dates = dict()
    object_number = ''
    infile = open(INPUTXML)
    outfile = open(OUTPUTXML, 'wb')
    csvfile = codecs.open(CSVFILENAME, 'r', encoding='utf-8-sig')
    csvreader = csv.DictReader(csvfile)
    main()

