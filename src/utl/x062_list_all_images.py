import argparse
import csv
import os.path
import re
import sys

from web.webutil import COLLECTION_PREFIX
from utl.cfg import DEFAULT_MDA_CODE

DESCRIPTION = """
    Examine one or more trees of folders recursively and print the filename, file size, and path
    of all images that have accession numbers in the filename.
    
    Output is a CSV file with the first column being the filename and subsequent columns
    being the containing folders.
"""

IMGFILES = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')

HOMEDIR = '/Users/mlg'


def one_file(parentpath, filename):
    global nimgs
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
        nimgs += 1
    return


def one_argument(indir):
    if '.git' in indir:
        return
    # print(f'{indir=}')
    for filename in os.listdir(indir):
        filepath = os.path.join(indir, filename)
        if os.path.isdir(filepath):
            if _args.exclude and filename == _args.exclude:
                continue
            one_argument(filepath)  # recursively walk subdirectory
        else:
            one_file(indir, filename)


def main():
    for arg in _args.indirs:
        one_argument(arg)


def print_table():
    global nrows
    maxlen = 0
    maxfn = ''
    for fn in sorted(table):
        if _args.nokeydir:
            if fn in keys:
                continue
        if _args.keydir:
            if fn not in keys:
                continue
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
        elif _args.nodups:
            found = False
            sizes = set()
            for i in range(2, len(row), 2):
                if row[i] in sizes:
                    found = True
                sizes.add(row[i])
            if found:
                continue
        csvwriter.writerow(table[fn])
        nrows += 1
    print(f'creating {_args.outfile} {maxfn=}, max files = {((maxlen - 1) // 2):}')


def getparser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('indirs', nargs='*', help='''
        One or more folders containing files to search.''')
    parser.add_argument('-o', '--outfile', required=True, help='''
        File to contain the output CSV file.''')
    parser.add_argument('--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code. The default is {DEFAULT_MDA_CODE}''')
    key_group = parser.add_mutually_exclusive_group()
    key_group.add_argument('-k', '--keydir', help=f'''
        Only write to output if the file is in this directory. ''')
    key_group.add_argument('-n', '--nokeydir', help=f'''
        Only write to output if the file is not in this directory. ''')
    dup_group = parser.add_mutually_exclusive_group()
    dup_group.add_argument('-p', '--dups', action='store_true', help='''
        Only write to output if there are multiple copies of the same file, determined
        by name and file size.
        ''')
    dup_group.add_argument('-q', '--nodups', action='store_true', help='''
        Only write to output if there are NOT multiple copies of the same file, determined
        by name and file size.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-x', '--exclude', help='''
        Exclude this folder and subfolders from the search.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


def read_keyfile(filename):
    print(f'{filename=}')
    for keyfile in os.listdir(filename):
        if os.path.isdir(os.path.join(filename, keyfile)):
            read_keyfile(os.path.join(filename, keyfile))
        else:
            if _args.verbose > 1:
                print(f'    {keyfile=}')
            keys.add(keyfile)


if __name__ == '__main__':
    assert sys.version_info >= (3, 13)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    table = dict()
    nrows = nimgs = 0
    csvfile = open(_args.outfile, 'w')
    csvwriter = csv.writer(csvfile)
    if _args.keydir or _args.nokeydir:
        keys = set()
        read_keyfile(_args.keydir if _args.keydir else _args.nokeydir)
        print(f'{len(keys)=}')
    main()
    print_table()
    print(f'End list_all_imgs. Rows created: {nrows}, with {nimgs} files.')
