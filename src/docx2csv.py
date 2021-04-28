"""
    Convert a DOCX file to CSV.
"""
import argparse
from docx import Document
import csv
import sys


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
    for table in tables:
        trace(2, 'Processing table {}', tablenumber)
        tablenumber += 1
        if _args.table and _args.table != tablenumber:
            trace(1, 'Skipping table {}', tablenumber)
            continue
        for i, row in enumerate(table.rows):  # read each row
            row_content = []
            for cell in row.cells:  # read all cells in a row
                c = cell.text
                row_content.append(c.strip())
            if not _args.inhibit_upper and len(row_content):
                row_content[0] = row_content[0].strip().upper()
            data.append(row_content)
    data_write_csv(data)


def getargs():
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
    parser.add_argument('-t', '--table', type=int, default=0, help='''
        Select a single table to process. The default is to process all tables.
        ''')
    parser.add_argument('-u', '--inhibit_upper', action='store_true',
                        default=False, help='''
        By default, the first column is converted to upper case and white
        space characters are removed.
        If specified, inhibit this conversion.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    _args = getargs()
    infile = open(_args.infile, 'rb')
    encoding = 'utf-8-sig' if _args.bom else 'utf-8'
    outfile = open(_args.outfile, 'w', encoding=encoding)
    main()
