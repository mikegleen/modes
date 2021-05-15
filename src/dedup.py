"""
    Copy an update file, removing rows that also occur in a base file.
"""
import argparse
import csv
import os
import sys


def main():
    infile = open(_args.infile)
    basefile = open(_args.basefile)
    basereader = csv.DictReader(basefile)
    base = set()
    for row in basereader:
        base.add(row['Serial'])
    outfile = open(_args.outfile, 'w')
    for row in infile:
        serial = row.strip()
        if serial in base:
            print(f'Skipping {serial}')
        else:
            print(serial, file=outfile)


def getargs():
    parser = argparse.ArgumentParser(description='''
    Copy an update file, removing rows that also occur in a base file.
        ''')
    parser.add_argument('infile', help='''
        The input CSV file''')
    parser.add_argument('outfile', help='''
        The output CSV file''')
    parser.add_argument('-b', '--basefile', required=True, help='''
        The file containing the existing numbers to not be output.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    nofinds = 0
    _args = getargs()
    main()
    basename = os.path.basename(sys.argv[0])
    print(f'End {basename.split(".")[0]}')
