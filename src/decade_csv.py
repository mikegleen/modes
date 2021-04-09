"""
    Add a column to a CSV file with the decade a work was created based on
    the 'Date Produced' column.
"""
import argparse
import codecs
import csv
import re
import sys
from utl.normalize import britishdatefrommodes, datefrommodes


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def decade(datestr):
    mat = re.match(r'.*(\d{4})$', datestr)
    dec = ''
    if mat:
        year = int(mat.group(1))
        dec = f'{(year // 10) * 10}s'
    return dec


def main():
    global nrows
    reader = csv.DictReader(incsvfile)
    r: list = list(reader.fieldnames)
    r.append('HumanDate')
    r.append('IsoDate')
    r.append('Decade')
    writer = csv.DictWriter(outfile, fieldnames=r)
    writer.writeheader()
    nrows = 0
    for row in reader:
        row['HumanDate'] = britishdatefrommodes(row['Date Produced'])
        try:
            dfm, _ = datefrommodes(row['Date Produced'])
            row['IsoDate'] = dfm.isoformat()
        except ValueError:
            row['IsoDate'] = 'unknown'
        row['Decade'] = decade(row['Date Produced'])
        # print(row)
        writer.writerow(row)
        nrows += 1


def getargs():
    parser = argparse.ArgumentParser(description='''
    Read a CSV file, recode one column and write the CSV file.
        ''')
    parser.add_argument('incsvfile', help='''
        The CSV file containing data to be inserted into the XML template.''')
    parser.add_argument('outfile', help='''
        The output CSV file.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    global nrows
    assert sys.version_info >= (3, 8)
    _args = getargs()
    incsvfile = codecs.open(_args.incsvfile, 'r', encoding='utf-8-sig')
    outfile = open(_args.outfile, 'w')
    trace(1, 'Input file: {}', _args.incsvfile)
    trace(1, 'Creating file: {}', _args.outfile)
    main()
    trace(1, 'End recode. {} object{} created.', nrows,
          '' if nrows == 1 else 's')
