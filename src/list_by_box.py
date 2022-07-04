# -*- coding: utf-8 -*-
"""
    Create a report of box contents.
    Parameters:
        1. Input XML file or CSV file.
           XML: This is a Modes database
           CSV: Heading is required. The first column is the serial number
                and the second column is the location. Typically this was
                produced by filtering the database by some prior criterion.
        2. Optional output CSV file. If omitted, output is to STDOUT.
"""
from collections import defaultdict
import csv
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.normalize import normalize_id, denormalize_id


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
        return f'{g1}{g2:03}'
    else:
        return loc


def unpad_loc(loc):
    m = re.match(r'(\D+)(\d+)', loc)
    if m:
        g1 = m.group(1).upper()
        g2 = int(m.group(2))
        return f'{g1}{g2}'
    else:
        return loc


def one_object(elt):
    num = elt.find('./ObjectIdentity/Number').text
    loc = elt.find('./ObjectLocation[@elementtype="current location"]/Location')
    if loc is not None and loc.text:
        location = pad_loc(loc.text)
    else:
        location = 'unknown'
    title = elt.find('./Identification/Title').text
    briefdes = elt.find('./Identification/BriefDescription').text
    if briefdes is None:
        briefdes = ''
    nnum = normalize_id(num)
    boxdict[location].append(nnum)
    titledict[nnum] = (title, briefdes)


def handle_csv():
    reader = csv.reader(infile)
    header = next(reader)
    print('CSV file header:', header)
    for row in reader:
        loc = pad_loc(row[1])
        nnum = normalize_id(row[0])
        boxdict[loc].append(nnum)


def handle_xml():
    for event, obj in ET.iterparse(infile):
        if obj.tag == 'Object':
            one_object(obj)
            obj.clear()


def main():
    if infile.name.lower().endswith('.csv'):
        handle_csv()
    else:
        handle_xml()
    for box in sorted(boxdict.keys()):
        writer.writerow([''])
        writer.writerow([''])
        writer.writerow([f'Box,{unpad_loc(box)}'])
        writer.writerow(['--------------'])
        for nnum in sorted(boxdict[box]):
            if nnum in titledict:
                writer.writerow([denormalize_id(nnum),
                                 f'{titledict[nnum][0]} ({titledict[nnum][1]})'])

    # print('Pictures already scanned', file=outfile)
    # print(f'Locations from {infile.name}', file=outfile)
    # print('========================', file=outfile)
    # for box in sorted(boxdict.keys()):
    #     print('\n', file=outfile)
    #     print(f'{unpad_loc(box)}', file=outfile)
    #     print('--------------', file=outfile)
    #     for nnum in sorted(boxdict[box]):
    #         if nnum in titledict:
    #             print(f'{denormalize_id(nnum)},{titledict[nnum][0]},'
    #                   f'{titledict[nnum][1]}', file=outfile)
    #         else:
    #             print(denormalize_id(nnum), file=outfile)


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    infile = open(sys.argv[1])
    # outfile = codecs.open(sys.argv[2], 'w', 'utf-8-sig')
    if len(sys.argv) < 3:
        outfile = sys.stdout
    else:
        outfile = open(sys.argv[2], 'w', newline='')
    writer = csv.writer(outfile)
    boxdict = defaultdict(list)
    titledict = dict()
    main()
