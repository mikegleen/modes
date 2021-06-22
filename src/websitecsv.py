"""
    Add a column to a CSV file with the decade a work was created based on
    the 'Date Produced' column.

    Merge the 'Exhibition Name' and 'Exhibition Place' columns producing a
    single column of Name (Place).
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
    r = list(reader.fieldnames[:3])  # Serial, Title, Medium, Date Produced
    r.append('Exhibition')
    r.append('HumanDate')
    r.append('IsoDate')
    r.append('Decade')
    writer = csv.DictWriter(outfile, fieldnames=r)
    writer.writeheader()
    nrows = 0
    for row in reader:
        newrow = dict()
        newrow['Serial'] = row['Serial']
        newrow['Title'] = row['Title']
        newrow['Medium'] = row['Medium']
        # newrow['Date Produced'] = row['Date Produced']
        newrow['HumanDate'] = britishdatefrommodes(row['Date Produced'])
        try:
            dfm, _ = datefrommodes(row['Date Produced'])
            newrow['IsoDate'] = dfm.isoformat()
        except ValueError:
            newrow['IsoDate'] = 'unknown'
        newrow['Decade'] = decade(row['Date Produced'])
        places = row['Exhibition Place'].split('|')
        names = row['Exhibition Name'].split('|')
        if len(places) != len(names):
            print(f'Exhibition name/place mismatch count: {row["Serial"]}')
            continue
        # print(row)
        exhibition = []
        for np in zip(names, places):
            exhibition.append(f'{np[0]}({np[1]})')
        newrow['Exhibition'] = '|'.join(exhibition)
        writer.writerow(newrow)
        nrows += 1


def getparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='''
    Read a CSV file, recode columns and write the CSV file. The Exhibition
    Name and Exhibition Place columns are merged into a "name(place)" format.
    The Date Produced column (in Modes format) is deleted and replaced by a
    human-friendly column and an ISO date column.''')
    parser.add_argument('incsvfile', help='''
        The CSV file containing data to be inserted into the XML template. The
        input is expected to have been produced by xml2csv.py using the
        website.yml config file.''')
    parser.add_argument('outfile', help='''
        The output CSV file.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary
        information.''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


if __name__ == '__main__':
    global nrows
    assert sys.version_info >= (3, 8)
    _args = getargs(sys.argv)
    incsvfile = codecs.open(_args.incsvfile, 'r', encoding='utf-8-sig')
    outfile = open(_args.outfile, 'w')
    trace(1, 'Input file: {}', _args.incsvfile)
    trace(1, 'Creating file: {}', _args.outfile)
    main()
    trace(1, 'End recode. {} object{} created.', nrows,
          '' if nrows == 1 else 's')
