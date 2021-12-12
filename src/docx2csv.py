"""
    Convert a DOCX file to CSV.
"""
import argparse
from docx import Document
import csv
import sys

from utl.normalize import sphinxify


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def data_write_csv(datas):
    writer = csv.writer(outfile)
    for data in datas:
        writer.writerow(data)


def main():
    tablenumber = 0
    document = Document(infile)  # Read in file
    tables = document.tables  # Get the table set in the file
    data = []
    index_column = _args.index_column
    index_row = _args.index_row
    index = _args.index_start
    for table in tables:
        trace(2, 'Processing table {}', tablenumber)
        tablenumber += 1
        if _args.table and _args.table != tablenumber:
            trace(1, 'Skipping table {}', tablenumber)
            continue
        for i, docrow in enumerate(table.rows):  # read each row
            row: list = []
            ncell = 0
            for j, cell in enumerate(docrow.cells):  # read all cells in a row
                c = cell.text
                if j == index_column and i >= index_row:
                    c = str(index)
                    index += 1
                row.append(c.strip())
            excol = _args.exclude_column
            if _args.exclude:
                if len(row) > excol and row[excol] == _args.exclude:
                    continue
            if not _args.inhibit_upper and len(row):
                row[0] = row[0].strip().upper()
            upcol = _args.upper
            if upcol and len(row) > upcol:
                row[upcol] = row[upcol].strip().upper()

            data.append(row)
    data_write_csv(data)


def getparser():
    parser = argparse.ArgumentParser(description='''
        Read a DOCX file, extract any tables, and convert them to CSV.
        ''')
    parser.add_argument('infile', help='''
        The input DOCX file''')
    parser.add_argument('outfile', help='''
        The output CSV file.''')
    parser.add_argument('-b', '--bom', action='store_true', help='''
        Select this option to insert a BOM at the front of the output CSV file.
        Use this option when the CSV file is to be imported into Excel so that
        the proper character set (UTF-8) is used.
        ''')
    parser.add_argument('--exclude_column', type=int, default=0,
                        help=sphinxify('''
        Specify the column to check for row exclusion. The default is
        column 0. This argument is ignored if --exclude is not specified.
        ''', called_from_sphinx))
    parser.add_argument('-i', '--index_column', type=int, help=sphinxify('''
        Specify a column to generate an index in. This will overwrite whatever
        is in that column
        ''', called_from_sphinx))
    parser.add_argument('-r', '--index_row', type=int, default=0,
                        help=sphinxify('''
        The zero-based row in which to begin generating the index. This is
        ignored unless --index_column is specified. The default is zero, that
        is, to start numbering from the first row.
        ''', called_from_sphinx))
    parser.add_argument('-s', '--index_start', type=int, default=1,
                        help=sphinxify('''
        The first number to insert into the index column. This is
        ignored unless --index_column is specified. The default is one which
        is incremented for each row.
        ''', called_from_sphinx))
    parser.add_argument('-t', '--table', type=int, default=0, help='''
        Select a single table to process. The default is to process all tables.
        ''')
    parser.add_argument('-u', '--inhibit_upper', action='store_true',
                        default=False, help='''
        By default, the first column is converted to upper case and white
        space characters are removed. If specified, inhibit this conversion.
        ''')
    parser.add_argument('--upper',type=int,
                        help='''
                        Convert the zero-based column to upper case. This is
                        in addition to column zero unless -u is specified.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-x', '--exclude', help=sphinxify('''
        Exclude rows where this text appears in the column specified by the
        --exclude_column argument.
        ''', called_from_sphinx))
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


called_from_sphinx = True


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    called_from_sphinx = False
    _args = getargs(sys.argv)
    infile = open(_args.infile, 'rb')
    if _args.bom:
        encoding = 'utf-8-sig'
    else:
        trace(1, 'BOM not written.')
        encoding = 'utf-8'
    outfile = open(_args.outfile, 'w', encoding=encoding)
    main()
