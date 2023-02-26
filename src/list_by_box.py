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
import argparse
from collections import defaultdict
import csv
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import expand_idnum
from utl.normalize import normalize_id, denormalize_id
from utl.normalize import sphinxify


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
    if not title:
        title = ''
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
        titledict[nnum] = ('', '')


def handle_xml():
    objectlevel = 0
    for event, elem in ET.iterparse(infile, events=('start', 'end')):
        # print(event)
        if event == 'start':
            # print(elem.tag)
            if elem.tag == 'Object':
                objectlevel += 1
            continue
        # It's an "end" event.
        if elem.tag != 'Object':
            continue
        objectlevel -= 1
        if objectlevel:
            continue  # It's not a top level Object.
        one_object(elem)
        elem.clear()


def writerow(row):
    if _args.outcsv:
        writer.writerow(row)
    else:
        print(' '.join(row), file=outfile)


def main():
    if infile.name.lower().endswith('.csv'):
        handle_csv()
    else:
        handle_xml()
    for box in sorted(boxdict.keys()):
        writerow([''])
        writerow([''])
        writerow(['Box', unpad_loc(box)])
        writerow(['--------------'])
        for nnum in sorted(boxdict[box]):
            # titledict[accn#] = (title, description)
            # print(titledict[nnum])
            comment = f'{titledict[nnum][0]} ({titledict[nnum][1]})'[:50]
            writerow([f'{denormalize_id(nnum):15}',
                      'scanned' if nnum in image_set else '       ', comment])


def getparser() -> argparse.ArgumentParser:
    """
    Called either by getargs() in this file or by Sphinx.
    :return: an argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser(description='''
    Read a CSV file, recode columns and write the CSV file. The Exhibition
    Name and Exhibition Place columns are merged into a "name at place" format
    unless the place is "HRM" in which case it's omitted.
    The DateBegin column (in Modes format) is deleted and replaced by a
    human-friendly column and an ISO date column.

    The input columns are defined in ``cfg/website.yml`` and must match
    names hard-coded here.''')
    parser.add_argument('inmodesfile', help=sphinxify('''
        Modes XML database file.
        ''', called_from_sphinx))
    parser.add_argument('-c', '--outcsv', action='store_true', help='''
        Output is formatted as a CSV file. If not selected, a text report is
        written.''')
    parser.add_argument('-i', '--imglist', help='''
        Text file with names of pictures already scanned.''')
    parser.add_argument('-o', '--outfile', type=argparse.FileType('w'),
                        default='-', help='''
        The output CSV file.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary
        information.''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


def get_imgset() -> set[str]:
    """

    :return: A set of normalized accession numbers from the imglist file.
    """
    imgset = set()
    if not _args.imglist:
        return imgset
    imgfile = open(_args.imglist)
    for row in imgfile:
        expanded = [normalize_id(obj) for obj in expand_idnum(row)]
        imgset.update(expanded)
    return imgset


called_from_sphinx = True


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    called_from_sphinx = False
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    infile = open(_args.inmodesfile)
    outfile = _args.outfile
    if _args.outcsv:
        writer = csv.writer(outfile)
    boxdict = defaultdict(list)
    titledict = dict()
    image_set = get_imgset()
    main()
