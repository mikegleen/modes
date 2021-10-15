"""
For every ID in a CSV file, report if the corresponding image is not in a
folder.
"""
import argparse
import csv
import os.path
import re
import sys
from utl.excel_cols import col2num
from utl.list_objects import list_objects
from utl.normalize import normalize_id, denormalize_id


def trace(level, template, *args):
    if VERBOSE >= level:
        print(template.format(*args))


def getargs():
    parser = argparse.ArgumentParser(description='''
    For every ID in a CSV file, report if the corresponding image is not in a
    folder.''')
    parser.add_argument('csvfile', help='''
        CSV file containing the list of new objects''')
    parser.add_argument('imgdir', help='''
        Folder containing folders containing images we already have''')
    parser.add_argument('--col_acc', help='''
        The zero-based column containing the accession number (ID) of the
        object we are searching for. The default is column zero. The column can
        be a number or a spreadsheet-style letter.''')
    parser.add_argument('--modesfile', help='''
        File to search for valid accession numbers.''')
    parser.add_argument('--imgreport', help='''
        File containing a list of the images that we have.''')
    parser.add_argument('--outfile', help='''
        Output file. Default is sys.stdout''')
    parser.add_argument('--skip_rows', type=int, default=0, help='''
        Skip rows at the beginning of the CSV file.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    if args.col_acc is None:
        args.col_acc = 0
    else:
        args.col_acc = col2num(str(args.col_acc))
    return args


def build_img_set():
    """
    Build a set of normalized accession numbers from the folders containing
    images.
    :return: The set of normalized numbers.
    """
    img_ids = set()
    for imgdir in os.listdir(_args.imgdir):
        dirpath = os.path.join(_args.imgdir, imgdir)
        if not os.path.isdir(dirpath):
            print('not directory:', imgdir)
        for imgfile in os.listdir(dirpath):
            m = re.match(r'(collection_)?(.*)', imgfile)
            imgfile = m.group(2)  # remove optional leading 'collection_'
            prefix, suffix = os.path.splitext(imgfile)
            if suffix.lower() not in ('.jpg', '.png'):
                print('not image:', imgfile)
                continue
            img_ids.add(normalize_id(prefix))
    return img_ids


def main():
    img_ids = build_img_set()
    idnums = set([x[0] for x in list_objects(_args.modesfile)])
    skiprows = _args.skip_rows
    reader = csv.reader(_args.csvfile)
    for n in range(skiprows):  # default = 0
        skipped = next(reader)  # skip header
        if _args.verbose >= 1:
            print(f'Skipping row in map file: {skipped}')
    col_acc = _args.col_acc
    for row in reader:
        idnum = row[col_acc]
        nid = normalize_id(idnum)
        if nid not in idnums:
            trace(2, 'Not in Modes: {}', nid)
            continue
        if nid in img_ids:
            trace(2, 'In image folder: {}', nid)
            continue
        print(idnum, file=outfile)


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    _args = getargs()
    if _args.outfile:
        outfile = open(_args.outfile, 'w')
    else:
        outfile = sys.stdout
    VERBOSE = _args.verbose
    main()
