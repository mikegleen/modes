"""
    Convert a DOCX file to CSV.
"""
import argparse
from docx import Document
import csv
import sys

from utl.excel_cols import col2num
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
    # Note that if a parameter is not specified, the default is None.
    index_column = _args.index_column
    index_row = _args.index_row
    index = _args.index_start
    prepend_index = index_column == '-1'
    upcol = _args.upper
    if upcol is not None and prepend_index:
        upcol += 1
    for table in tables:
        tablenumber += 1
        numrows = 0
        trace(2, 'Processing table {}', tablenumber)
        if _args.table and _args.table != tablenumber:
            trace(1, 'Skipping table {}', tablenumber)
            continue
        for i, docrow in enumerate(table.rows):  # read each row
            row: list = []
            if prepend_index:
                if i >= index_row:
                    row.append(str(index))
                    index += 1
                else:
                    row.append('Index')
            data_in_row = False
            for j, cell in enumerate(docrow.cells):  # read all cells in a row
                c = cell.text.strip()
                if c:
                    data_in_row = True
                    if not _args.include_lf:
                        c = ' '.join(c.split())  # remove line feeds
                if j == index_column and i >= index_row:
                    c = str(index)
                    index += 1
                row.append(c.strip())
            excol = _args.exclude_column
            if _args.exclude:
                if len(row) > excol and row[excol] == _args.exclude:
                    continue
            if not _args.inhibit_upper and len(row):
                uc = 1 if prepend_index else 0
                row[uc] = row[uc].strip().upper()
            if upcol is not None and len(row) > upcol:
                row[upcol] = row[upcol].strip().upper()
            if data_in_row or _args.include_blank:
                data.append(row)
                numrows += 1
            else:
                index -= 1
        trace(1, 'table {}: {} rows written.', tablenumber, numrows)
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
        Insert a BOM at the front of the output CSV file.
        Use this option when the CSV file is to be imported into Excel so that
        the proper character set (UTF-8) is used.
        ''')
    parser.add_argument('-x', '--exclude', help=sphinxify('''
        Exclude rows where this text appears in the column specified by the
        --exclude_column argument.
        ''', called_from_sphinx))
    parser.add_argument('--exclude_column', type=str, default='0',
                        help=sphinxify('''
        Specify the column to check for row exclusion. The default is
        column 0. This argument is ignored if --exclude is not specified.
        ''', called_from_sphinx))
    parser.add_argument('--include_blank', action='store_true',
                        help=sphinxify('''
        Normally completely blank rows will be excluded. If specified, they
        will be included.
        ''', called_from_sphinx))
    parser.add_argument('--include_lf', action='store_true',
                        help=sphinxify('''
        Normally line feeds will be converted to spaces. If specified, this is
        not done.
        ''', called_from_sphinx))
    parser.add_argument('-i', '--index_column', type=str, help=sphinxify('''
        Specify a column to generate an index in. This will overwrite whatever
        is in that column. If you specify -1, a column will be prepended to the
        existing row. The column can be a number or a spreadsheet-style letter.
        ''', called_from_sphinx))
    parser.add_argument('-r', '--index_row', type=int, default=0,
                        help=sphinxify('''
        The zero-based row in which to begin generating the index. This is
        ignored unless --index_column is specified. The default is zero, that
        is, to start numbering from the first row. The column can be a number
        or a spreadsheet-style letter. ''', called_from_sphinx))
    parser.add_argument('-s', '--index_start', type=int, default=1,
                        help=sphinxify('''
        The first number to insert into the index column. This is
        ignored unless --index_column is specified. The default is one which
        is incremented for each row. In other words, row zero, the first row,
        will be given number one, and so on.
        ''', called_from_sphinx))
    parser.add_argument('-t', '--table', type=int, default=0, help='''
        Select a single table to process. The default is to process all tables.
        ''')
    parser.add_argument('-u', '--inhibit_upper', action='store_true',
                        default=False, help='''
        By default, the first column is converted to upper case and white
        space characters are removed. If specified, inhibit this conversion.
        ''')
    parser.add_argument('--upper', type=int,
                        help='''
                        Convert the zero-based column to upper case. This is
                        in addition to column zero unless -u is specified.
                        Column zero is the first column in the input row.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if args.index_column is not None:
        if args.index_column != '-1':
            try:
                args.index_column = col2num(args.index_column)
            except ValueError as err:
                print(f'Invalid --index_column value: "{err}"\nAborting.')
                sys.exit()
        else:
            args.index_column = -1
    args.exclude_column = col2num(args.exclude_column)
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
