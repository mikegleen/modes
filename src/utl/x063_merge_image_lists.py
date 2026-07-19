import argparse
import csv
import sys

DESCRIPTION = """
    Input is two files created by x062_list_all_images.py.
    Output is a single file with the rows merged.
"""


def main():
    for filename in [_args.infile1, _args.infile2]:
        incsvfile = open(filename)
        reader = csv.reader(incsvfile)
        nrow = 0
        for row in reader:
            nrow += 1
            if row[0] not in table:
                table[row[0]] = row
            else:
                table[row[0]] += row[1:]
        print(f'file {filename}: {nrow} rows')
    incsvfile.close()

    outcsvfile = open(_args.outfile, 'w')
    csvwriter = csv.writer(outcsvfile)
    maxlen = 0
    maxfn = ''
    nwritten = 0
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
        csvwriter.writerow(row)
        nwritten += 1
    print(f'{maxfn=}, {maxlen=}, {nwritten=}')


def getparser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('infile1', help='''
        file to merge.''')
    parser.add_argument('infile2', help='''
        another file to merge.''')
    parser.add_argument('outfile', help='''
        File to contain the output CSV file.''')
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
    main()
