import argparse
import os.path
import re
import sys

DESCRIPTION = """
    In filenames of scanned images, pad the page numbers to three places with leading zeros.
"""

IMGFILES = ('.jpg', '.jpeg', '.png')

PAT = r'([^-]*-[^-]*-)(\d+)(A|B)?\.jpg'


def one_file(parentpath, filename):
    prefix, suffix = os.path.splitext(filename)
    if suffix.lower() not in IMGFILES:
        if filename != '.DS_Store':  # MacOS magic file
            print(f'Skipping not image: {filename}')
        return
    m = re.match(PAT, filename)
    if m is None:
        # print(f"No match filename {filename}")
        return
    # print(m)
    oldfullpath = os.path.join(parentpath, filename)
    page = int(m[2])
    face = m[3] if m[3] else ''
    fn = f'{m[1]}{page:03}{face}.jpg'
    newfullpath = os.path.join(parentpath, fn)
    print(oldfullpath, '-->', newfullpath)
    if _args.rename:
        os.rename(oldfullpath, newfullpath)


def main(indir):
    for file in os.listdir(indir):
        filepath = os.path.join(indir, file)
        if os.path.isdir(filepath):
            main(filepath)  # recursively walk subdirectory
        else:
            one_file(indir, file)


def getparser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('indir', help='''
        Folder containing files to update or sub-folders.''')
    parser.add_argument('-r', '--rename', action='store_true', help='''
        Rename the files. If omitted, only print the actions that would have been taken.
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
    main(_args.indir)
