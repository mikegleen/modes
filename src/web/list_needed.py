"""
For every ID in a CSV file or XML file, report if the corresponding image is not in a
folder.

The CSV file can be created from a folder using dir2csv.py.
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
    parser.add_argument('imgdir', help='''
        Folder containing images or subfolders containing images we already
        have. Only one level of subfolder is examined.''')
    parser.add_argument('-c', '--candidatefile', help='''
        CSV file containing the list of new objects or a directory containing
        jpg files with names consisting of the accession numbers.''')
    parser.add_argument('--col_acc', type=int, default=0, help='''
        The zero-based column containing the accession number (ID) of the
        object we are searching for. The default is column zero.''')
    parser.add_argument('-i', '--invert', action='store_true', help='''
        Report if the image **IS** in the folder.''')
    parser.add_argument('-m', '--modesfile', help='''
        File to search for valid accession numbers.''')
    parser.add_argument('-r', '--reportfile', help='''
        File containing a list of the images that we have.''')
    parser.add_argument('--outfile', help='''
        Output file. Default is sys.stdout''')
    parser.add_argument('-s', '--skip_rows', type=int, default=0, help='''
        Skip rows at the beginning of the CSV file.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    if args.col_acc is None:
        args.col_acc = 0
    else:
        args.col_acc = col2num(str(args.col_acc))
        print(f'{args.col_acc=}')
    return args


def build_img_set(candidates: set):
    """
    Build a set of normalized accession numbers from the folders containing
    images.
    :return: The set of normalized numbers.
    """
    def onefile(imgf: str):
        m = re.match(r'(collection_)?(.*)', imgf)
        imgf2 = m.group(2)  # remove optional leading 'collection_'
        prefix, suffix = os.path.splitext(imgf2)
        if suffix.lower() not in ('.jpg', '.png'):
            if suffix.lower() != '.txt':
                print('not image:', imgf)
            return
        try:
            nid = normalize_id(prefix)
        except ValueError as ve:
            print(f'Skipping {imgf}')
            return
        if nid in img_ids:
            print(f'Duplicate: {prefix} in {dirpath}')
        else:
            img_ids.add(nid)
            if reportfile and nid in candidates:
                print(prefix, file=reportfile)

    reportfile = open(_args.reportfile, 'w') if _args.reportfile else None
    img_ids = set()
    for imgdir in os.listdir(_args.imgdir):
        dirpath = os.path.join(_args.imgdir, imgdir)
        if not os.path.isdir(dirpath):
            onefile(imgdir)
            continue
        trace(1, 'Folder {}', dirpath)
        for imgfile in os.listdir(dirpath):
            if os.path.isdir(imgfile):
                print('Directory skipped', imgfile)
                continue
            onefile(imgfile)
    return img_ids


def build_candidate_set(valid_idnums):

    def add_one_id(candidate):
        nonlocal notinmodes
        try:
            normid = normalize_id(candidate)
        except ValueError as ve:
            trace(1, '{}', ve)
            return
        if normid in valid_idnums:
            candidate_set.add(normid)
        else:
            notinmodes += 1

    notinmodes = 0
    candidate_set = set()
    trace(2, "Building candidate set.")
    if os.path.isdir(_args.candidatefile):
        candidates = [os.path.splitext(f)[0] for f in os.listdir()]
        for c in candidates:
            add_one_id(c)
    else:
        reader = csv.reader(open(_args.candidatefile))
        for n in range(_args.skip_rows):  # default = 0
            skipped = next(reader)  # skip header
            trace(1, 'Skipping row in CSV file: {}', skipped)
        col_acc = _args.col_acc
        for row in reader:
            idnum = row[col_acc]
            if not idnum:
                continue
            add_one_id(idnum)

    if notinmodes:
        trace(1, '{} accession numbers skipped, not in Modes.', notinmodes)
    return candidate_set


def main():
    # x.normalized extracts the first entry in the namedtuple Obj_id.
    # valid_idnums is a set of all the IDs in the XML file
    valid_idnums = set([x.normalized for x in list_objects(_args.modesfile)])
    if _args.candidatefile:
        candidate_set = build_candidate_set(valid_idnums)
    else:
        candidate_set = valid_idnums
    img_ids = build_img_set(candidate_set)
    for nid in candidate_set:
        if _args.invert:
            if nid not in img_ids:
                trace(2, 'Not in image folder: {}', nid)
                continue
        else:
            if nid in img_ids:
                trace(2, 'In image folder: {}', nid)
                continue
        print(denormalize_id(nid), file=outfile)


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    _args = getargs()
    if _args.verbose < 2:
        sys.tracebacklimit = 0
    if _args.outfile:
        outfile = open(_args.outfile, 'w')
    else:
        outfile = sys.stdout
    VERBOSE = _args.verbose
    main()
