"""
    Rename files: 'd{3}.*.jpg' -> '<preface>\1.jpg'

    In folder JB1224_01, file 038.jpg becomes JB1224-038.jpg
"""
import argparse
import os.path
import re
import sys


def main():
    indir = _args.indir
    basename = os.path.basename(indir)
    basename = basename.split('_')[0]  # remove text like JB1224_01 -> JB1224
    files = os.listdir(indir)

    for fn in files:
        m = re.fullmatch(r'\d{3}.*\.(jpg|jpeg)', fn)
        if not m:
            print(f'Skipping: {fn}')
            continue
        newfn = f'{basename}-{fn}'
        src = os.path.join(indir, fn)
        dst = os.path.join(indir, newfn)
        print(f'{src}, {dst}')
        if not _args.dryrun:
            os.rename(src, dst)


def getparser():
    parser = argparse.ArgumentParser(description='''
        For every JPG file in a directory prepend the name of the folder
        including everything up to but not including the first "_" character.
        ''')
    parser.add_argument('indir', help='''
        Folder containing files to update''')
    parser.add_argument('-d', '--dryrun', action='store_true', help='''
        Noramlize the accession number written to the CSV file.
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
    assert sys.version_info >= (3, 11)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    print('Begin fix_dir_subnums.')
    main()
    print('End fix_dir_subnums.')
