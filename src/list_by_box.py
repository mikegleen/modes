# -*- coding: utf-8 -*-
"""
    Create a CSV file with the objects'
"""
import codecs
import csv
import html
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def pad_loc(loc):
    """
    If the location field matches the pattern "<Letter(s)><Number(s)>" like
    "S1" then pad the number part so that it sorts correctly. Also convert the
    letter part to upper case
    :param loc: location
    :return: padded location
    """
    m = re.match(r'(\D+)(\d+)', loc)
    if m:
        g1 = m.group(1).upper()
        g2 = int(m.group(2))
        return f'{g1}{g2:02}'
    else:
        return loc


def one_object(elt):
    num = elt.find('./ObjectIdentity/Number').text
    loc = elt.find('./ObjectLocation[@elementtype="current location"]/Location')
    if loc is not None and loc.text:
        location = loc.text
    else:
        location = 'unknown'
    title = elt.find('./Identification/Title').text
    if title:
        pass
        title = title.replace('\u0091', '‘')  # 145
        title = title.replace('\u0092', '’')
        title = title.replace('\u0093', '“')
        title = title.replace('\u0094', '”')
        title = title.replace('\u0096', '–')
        # title = title.encode('ascii', 'xmlcharrefreplace')
        # # if b'Roberson' in title:
        # #     print(title)
        # title = str(title)
        # title = title.replace('&#147;', '')
        # title = title.replace('&#148;', '')
        # title = html.unescape(title)
        # # if 'Roberson' in title:
        # #     print(title)
    row = [pad_loc(location), num, location, title]
    writer.writerow(row)


def main():
    for event, obj in ET.iterparse(infile):
        if obj.tag == 'Object':
            one_object(obj)
            obj.clear()


if __name__ == '__main__':
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    infile = open(sys.argv[1])
    # outfile = codecs.open(sys.argv[2], 'w', 'utf-8-sig')
    outfile = open(sys.argv[2], 'w', newline='')
    writer = csv.writer(outfile)
    main()
