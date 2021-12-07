"""
    Read a directory of JPEG files and create a CSV file with one column
    containing the filename minus the trailing .jpg
    A heading row of 'Serial' precedes the data.
"""
import argparse
import os.path
import re
import sys


def dir2csv(jpegdir):
    jpglist = list()
    jpgfiles = os.listdir(jpegdir)
    for jpgfile in jpgfiles:
        m = re.match(r'(collection_)?(.+)\.jpg', jpgfile)
        if not m:
            print(f'dir2csv skipping: {jpgfile}')
            continue
        jpglist.append(m.group(2))
    return sorted(jpglist)


def getargs():
    parser = argparse.ArgumentParser(description='''
    For every ID in a CSV file, report if the corresponding image is not in a
    folder.''')
    parser.add_argument('indir', help='''
        Folder containing images to list''')
    parser.add_argument('csvfile', help='''
        CSV file containing the accession numbers extracted from the filenames
        in imgdir''')
    parser.add_argument('--heading', action='store_true', help='''
        Write a row at the front of the CSV file containing 'Serial'.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    _args = getargs()
    indir = _args.indir
    outfile = open(_args.csvfile, 'w')

    outlist = dir2csv(indir)
    nout = 0
    if _args.heading:
        print('Serial', file=outfile)
    for fn in outlist:
        print(fn, file=outfile)
        nout += 1
    print(f'End dir2csv. {nout} rows written to {_args.csvfile}.')
