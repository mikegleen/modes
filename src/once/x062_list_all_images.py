import argparse
import csv
import os.path
import re
import sys

from web.webutil import COLLECTION_PREFIX
from utl.normalize import DEFAULT_MDA_CODE

DESCRIPTION = """
    Examine a tree of folders recursively and print the filename, file size, and path
    of all images that have accession numbers in the filename.
    
    Output is a CSV file with the first column being the filename and subsequent columns
    being the containing folders.
"""

IMGFILES = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')

HOMEDIR = '/Users/mlg'


def one_file(parentpath, filename):
    prefix, suffix = os.path.splitext(filename)
    if suffix.lower() not in IMGFILES:
        return
    rootfn = prefix.removeprefix(COLLECTION_PREFIX)
    if rootfn.startswith(_args.mdacode) or re.match(r'((JB)|(SH)|L)\d+', rootfn):
        # print(f'{filename},{os.path.join(parentpath, filename)}')
        #     return
        # if re.match(r'^((JB)|(SH)|L)\d+', rootfn):
        # print(f'{filename},{parentpath}')
        if filename not in table:
            table[filename] = [filename]
        fullpath = os.path.join(parentpath, filename)
        filesize = os.path.getsize(fullpath)

        # table[filename].append(parentpath)
        table[filename] += [parentpath.replace(HOMEDIR, '~'), filesize]
    return


def main(indir):
    for file in os.listdir(indir):
        filepath = os.path.join(indir, file)
        if os.path.isdir(filepath):
            if file == "2023-10-22_high_res_images":
                continue
            main(filepath)  # recursively walk subdirectory
        else:
            one_file(indir, file)


def print_table():
    maxlen = 0
    maxfn = ''
    for fn in sorted(table):
        if len(table[fn]) > maxlen:
            maxlen = len(table[fn])
            maxfn = fn
        csvwriter.writerow(table[fn])
    print(f'{maxfn=}, {maxlen=}')


def getparser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('indir', help='''
        Folder containing files to search.''')
    parser.add_argument('outfile', help='''
        File to contain the output CSV file.''')
    parser.add_argument('-m', '--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code. The default is {DEFAULT_MDA_CODE}''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 13)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    table = dict()
    csvfile = open(_args.outfile, 'w')
    csvwriter = csv.writer(csvfile)
    main(_args.indir)
    print_table()
