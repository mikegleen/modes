"""
    Input is a folder containing files.
    Output is a folder containing the files listed in the input CSV file.

    Only image files are copied
"""
import argparse
import os
import shutil
import sys

from utl.normalize import sphinxify, if_not_sphinx, DEFAULT_MDA_CODE
from utl.readers import row_list_reader

IMGFILES = ('.jpg', '.jpeg', '.png')
COLLECTION_PREFIX = 'collection_'


def s(i: int):
    return '' if i == 1 else 's'


def getparser():
    parser = argparse.ArgumentParser(description=sphinxify('''
        Extract files from a folder that match the list in the mapfile.
        File names in the folder may have a preamble of "collection_"
        ''', called_from_sphinx))
    parser.add_argument('-i', '--indir', required=True, help='''
        The input folder''')
    parser.add_argument('-o', '--outdir', help='''
        The output folder.''')
    parser.add_argument('-m', '--mapfile', required=True, help=sphinxify('''
            Required. The CSV or XLSX file containing the list of accession
            numbers corresponding to the files in the directory to copy.
            ''', called_from_sphinx))
    parser.add_argument('--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code, used in normalizing the accession number.''' +
                        if_not_sphinx(''' The default is "{DEFAULT_MDA_CODE}".
                        ''', called_from_sphinx))
    parser.add_argument('-s', '--skiprows', type=int, default=0, help='''
        Number of lines to skip at the start of the mapfile''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if not args.outdir:
        print('Dry run. No output written')
    return args


def main():
    indir = _args.indir
    for filename in os.listdir(indir):
        prefix, suffix = os.path.splitext(filename)
        if suffix.lower() not in IMGFILES:
            if filename != '.DS_Store':
                print(f'Skipping not image: {filename}')
            continue
        accname = prefix.removeprefix(COLLECTION_PREFIX)
        # print(f'{accname=}')
        if accname in fileset:
            fileset.remove(accname)
            inpath = os.path.join(indir, filename)
            if _args.verbose > 1:
                print(f'copy {inpath}')
            if not _args.outdir:
                continue
            shutil.copy2(inpath, _args.outdir)
    for accname in fileset:
        print(f'Not found: {accname}')


def getfileset():
    fs = set()
    csvreader = row_list_reader(_args.mapfile, skiprows=_args.skiprows)
    for row in csvreader:
        anum = row[0]
        # print(anum)
        if not anum:
            print(f'Skipping empty row')
            continue
        anum = anum.upper()
        if anum[0].isnumeric():
            anum = _args.mdacode + '.' + anum
        fs.add(anum)
    return fs


called_from_sphinx = True
if __name__ == '__main__':
    assert sys.version_info >= (3, 11)
    called_from_sphinx = False
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    fileset = getfileset()
    # print(fileset)
    main()
