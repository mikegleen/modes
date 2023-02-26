"""
List every file in a directory and its subdirectories marking any that are
duplicates in that tree.

Directories are processed in alphabetical order.

"""
import argparse
import csv
import os.path
import re
import sys

from utl.excel_cols import col2num
from utl.normalize import normalize_id


def trace(level, template, *args):
    if VERBOSE >= level:
        print(template.format(*args))


def getparser():
    parser = argparse.ArgumentParser(description='''
    List every file in a directory and its subdirectories marking any that are
    duplicates in that tree.

    Directories are processed in alphabetical order.
    ''')
    parser.add_argument('imgdir', help='''
        Folder containing images or subfolders containing images we already
        have.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
    Include filenames even if they are not valid accession numbers. This is
    useful in the case of multiple partial scans of a single picture. They
    would appear as, for example, ''')
    parser.add_argument('--col_exclude', type=str, default='0', help='''
    The zero-based column containing the accession number of the
    object to be excluded. The default is column zero. The column can be a
    number or a spreadsheet-style letter.
    ''')
    parser.add_argument('-e', '--exclude', help='''
    A CSV file containing accession numbers  to be excluded from the
    output list.''')
    parser.add_argument('-f', '--list_files', action='store_true', help='''
    Output the filename in addition to the accession number.''')
    parser.add_argument('-o', '--outfile', help='''
        Output file for the list of files. Default is sys.stdout. The warning
        messages are always written to sys.stdout.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    args.col_exclude = col2num(args.col_exclude)
    return args


def handle_folder(img_ids: dict, imgdir: str):
    """
    Build a set of normalized accession numbers from the folders containing
    images.
    :return: The set of normalized numbers.
    """
    def onefile(imgf: str):
        global nexcluded
        m = re.match(r'(collection_)?(.*)', imgf)
        imgf2 = m.group(2)  # remove optional leading 'collection_'
        prefix, suffix = os.path.splitext(imgf2)
        if suffix.lower() not in ('.jpg', '.png'):
            if _args.verbose > 2 or _args.verbose > 1 and imgf != '.DS_Store':
                print('not image:', imgf)
            return
        try:
            nid = normalize_id(prefix)
        except ValueError:
            if _args.all:
                img_ids[prefix] = (imgf2, dirpath)
            else:
                print(f'Skipping {imgf}')
            return
        if nid in excludes:
            nexcluded += 1
            return
        if nid in img_ids and _args.verbose > 0:
            print(f'Duplicate: {prefix} in {dirpath.removeprefix(_args.imgdir)},'
                  f' original in {img_ids[nid][1].removeprefix(_args.imgdir)}')
        else:
            img_ids[nid] = (imgf2, dirpath)

    for subfile in sorted(os.listdir(imgdir)):
        dirpath = os.path.join(imgdir, subfile)
        if os.path.isdir(dirpath):
            trace(1, 'Folder {}', dirpath)
            handle_folder(img_ids, dirpath)
        else:
            onefile(subfile)
            continue
    return img_ids


def main():
    img_ids = dict()
    handle_folder(img_ids, _args.imgdir)
    for key in sorted(img_ids.keys()):
        fname = img_ids[key][0]
        prefix, _ = os.path.splitext(fname)
        if _args.list_files:
            print(f'{prefix},{img_ids[key][1]}', file=outfile)
        else:
            print(prefix, file=outfile)
    trace(2, '{} image files found.', len(img_ids))


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    nexcluded = 0
    _args = getargs(sys.argv)
    if not os.path.isdir(_args.imgdir):
        raise ValueError(f'{_args.imgdir} is not a directory.')
    if _args.verbose < 2:
        sys.tracebacklimit = 0
    VERBOSE = _args.verbose
    if _args.outfile:
        outfile = open(_args.outfile, 'w')
    else:
        outfile = sys.stdout
    excludes = set()
    if _args.exclude:
        exfile = open(_args.exclude)
        exreader = csv.reader(exfile)
        for row in exreader:
            if _args.verbose > 2:
                print(f'{row=}')
            excludes.add(normalize_id(row[_args.col_exclude]))
    main()
    print(f'{nexcluded} excluded.')
