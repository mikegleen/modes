# -*- coding: utf-8 -*-
"""
    Create a report of box contents.
    Parameters:

    1. Input XML file or CSV file.
       XML:  This is a Modes database.
       CSV:  Heading is required. The first column is the serial number
       and the second column is the location. Typically, this was
       produced by filtering the database by some prior criterion.
    2. Optional output CSV file. If omitted, output is to STDOUT.

"""
import argparse
from collections import defaultdict
import csv
import re
import sys

from utl.cfgutil import expand_idnum
from utl.readers import read_include_dict
from utl.excel_cols import col2num
from utl.normalize import normalize_id, denormalize_id
from utl.normalize import sphinxify, if_not_sphinx
from utl.readers import object_reader


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


def one_xml_object(elt):
    num = elt.find('./ObjectIdentity/Number').text
    if _args.verbose  > 1:
        print(f'accession number: {num}')
    nnum = normalize_id(num)
    if includes:
        if nnum not in includes:
            return
    loc = elt.find('./ObjectLocation[@elementtype="current location"]/Location')
    if loc is None or not loc.text:
        location = 'unknown'
    else:
        location = pad_loc(loc.text)
    if _args.box and location.upper() != _args.box:
        return
    title_elt  = elt.find('./Identification/Title')
    if title_elt is not None:
        title = title_elt.text
    else:
        title = ''
    briefdes_elt = elt.find('./Identification/BriefDescription')
    if briefdes_elt is not None:
        briefdes = briefdes_elt.text
    else:
        briefdes = ''
    if briefdes is None:
        briefdes = ''
    boxdict[location].append(nnum)
    titledict[nnum] = (title, briefdes)


def handle_csv():
    reader = csv.reader(open(_args.infile))
    header = next(reader)
    print('CSV file header:', header)
    for row in reader:
        loc = pad_loc(row[1])
        nnum = normalize_id(row[0])
        boxdict[loc].append(nnum)
        titledict[nnum] = ('', '')


def handle_xml():
    for _, elem in object_reader(_args.infile):
        one_xml_object(elem)
        elem.clear()


def writerow(row):
    if _args.outcsv:
        writer.writerow(row)
    else:
        print(' '.join(row), file=outfile)


def main():
    scanned = 'scanned'
    notscanned = ' ' * len(scanned)
    if _args.infile.endswith('.csv'):
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
            if image_set:
                writerow([f'{denormalize_id(nnum):15}',
                         scanned if nnum in image_set else notscanned, comment])
            else:
                writerow([f'{denormalize_id(nnum):15}', comment])


def getparser() -> argparse.ArgumentParser:
    """
    Called either by getargs() in this file or by Sphinx.
    :return: an argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser(description='Create a report of box contents.')
    parser.add_argument('infile', help=sphinxify('''
        Modes XML database file or CSV file. If XML, this is a Modes database. If CSV,
        heading is required. The first column is the serial number
        and the second column is the location. Typically, this was
        produced by filtering the database by some prior criterion.        
        ''', called_from_sphinx))
    parser.add_argument('-b', '--box', help='''
        If selected, a single named box will be displayed. The name is case insensitive.''')
    parser.add_argument('-c', '--outcsv', action='store_true', help='''
        Output is formatted as a CSV file. If not selected, a text report is
        written.''')
    parser.add_argument('-i', '--imglist', help='''
        Text file with accession numbers of pictures already scanned. The script will add a note
        next to each accession number if that image has been scanned.''')
    parser.add_argument('--include', required=False, help='''
        A CSV file specifying the accession numbers of objects to be processed.
        If omitted, all records will be processed.''')
    parser.add_argument('--include_column', required=False,
                        default='0', type=str, help=
                        '''
        The column number containing the accession number in the file
        specified by the --include option.
        The column can be a number or a spreadsheet-style letter.''' +
                        if_not_sphinx(f''' The default is 0, the first column.''',
                                      called_from_sphinx))

    parser.add_argument('--include_skip', type=int, default=0, help='''
        The number of rows to skip at the front of the include file.''' +
                        if_not_sphinx(f''' The default is 0.
        ''', called_from_sphinx))
    parser.add_argument('-o', '--outfile', type=argparse.FileType('w'),
                        default='-', help=sphinxify('''
        The output text or CSV file. The default is to print to STDOUT. See --outcsv.''', called_from_sphinx))
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary
        information.''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    args.include_column = col2num(args.include_column)
    if args.box:
        args.box = pad_loc(args.box).upper()
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
    outfile = _args.outfile
    if _args.outcsv:
        writer = csv.writer(outfile)
    boxdict = defaultdict(list)
    titledict = dict()
    image_set = get_imgset()
    includes = read_include_dict(_args.include, _args.include_column,
                                 _args.include_skip, allow_blanks=True)
    main()
