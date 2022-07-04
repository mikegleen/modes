# -*- coding: utf-8 -*-
"""

"""
import argparse
import codecs
import csv
import sys


from utl.normalize import sphinxify


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def add_row(row):
    pass


def main():
    global nrows
    reader = csv.DictReader(incsvfile)
    trace(1, 'CSV Column Headings: {}', reader.fieldnames)
    nrows = 0
    for row in reader:
        emit = True
        if emit:
            nrows += 1
            add_row(row)
    if not _args.noprolog:
        outfile.write(b'</Interchange>')


def getparser():
    parser = argparse.ArgumentParser(description=sphinxify('''
        Read a CSV file containing two  columns. The first column
        is the accession number and the second column contains text. 
                ''', calledfromsphinx))
    parser.add_argument('-i', '--incsvfile', help='''
        The CSV file containing data to be inserted into the DOCX file.
        ''')
    parser.add_argument('-o', '--outfile', help='''
        The output DOCX file.''')
    parser.add_argument('-p', '--page', action='store_true', help='''
        Eject a page for each new section.''')
    parser.add_argument('--section', help='''
        Specify text in the first column that indicates a new section.
        ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


calledfromsphinx = True


if __name__ == '__main__':
    global nrows
    assert sys.version_info >= (3, 9)
    calledfromsphinx = False
    _args = getargs(sys.argv)
    incsvfile = codecs.open(_args.incsvfile, 'r', encoding='utf-8-sig')
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}', _args.incsvfile)
    trace(1, 'Creating file: {}', _args.outfile)
    main()
    trace(1, 'End csv2xml. {} object{} written.', nrows,
          '' if nrows == 1 else 's')
