# -*- coding: utf-8 -*-
"""
    Create a CSV file with the object location as the first field.
    Parameters:
        1. Input XML file
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

    nnum = normalize_id(num)
    boxdict[location].append(nnum)
    titledict[nnum] = title


def main():
    for event, obj in ET.iterparse(infile):
        if obj.tag == 'Object':
            one_object(obj)
            obj.clear()
    for box in sorted(boxdict.keys()):
        writer.writerow([''])
        writer.writerow([''])
        writer.writerow([f'Box {unpad_loc(box)}'])
        writer.writerow(['--------------'])
        for nnum in sorted(boxdict[box]):
            writer.writerow([denormalize_id(nnum), titledict[nnum]])


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
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
