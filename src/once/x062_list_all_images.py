import argparse
import csv
import os.path
import re
import sys

from web.webutil import COLLECTION_PREFIX
from utl.cfg import DEFAULT_MDA_CODE

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


def one_argument(indir):
    if '.git' in indir:
        return
    # print(f'{indir=}')
    for file in os.listdir(indir):
        filepath = os.path.join(indir, file)
        if os.path.isdir(filepath):
            # if file == "2023-10-22_high_res_images":
            #     continue
            one_argument(filepath)  # recursively walk subdirectory
        else:
            one_file(indir, file)


def main():
    for arg in _args.indirs:
        one_argument(arg)


def print_table():
    maxlen = 0
    maxfn = ''
    for fn in sorted(table):
        row = table[fn]
        if len(row) > maxlen:
            maxlen = len(row)
            maxfn = fn
        if _args.dups:
            found = False
            sizes = set()
            for i in range(2, len(row), 2):
                if row[i] in sizes:
                    found = True
                sizes.add(row[i])
            if not found:
                continue
        csvwriter.writerow(table[fn])
    print(f'{maxfn=}, {maxlen=}')


def getparser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('indirs', nargs='*', help='''
        Folder containing files to search.''')
    parser.add_argument('-o', '--outfile', help='''
        File to contain the output CSV file.''')
    parser.add_argument('-m', '--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code. The default is {DEFAULT_MDA_CODE}''')
    parser.add_argument('-p', '--dups', action='store_true', help='''
        Only write to output if there are multiple copies of the same file, determined
        by name and file size.
        ''')
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
    main()
    print_table()
