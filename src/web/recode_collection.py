"""
    Add a column to a CSV file with the decade an object was created based on
    the 'DateBegin' column which came from ./Production/Date/DateBegin.

    Merge the 'Exhibition Name' and 'Exhibition Place' columns producing a
    single column of "<name> at <place>".

    Input is the CSV file produced by csv2xml.py using website.yml
    Output is a reformatted CSV file.
"""
import argparse
import codecs
import csv
import re
import sys
from utl.normalize import britishdatefrommodes
from utl.normalize import isoformatfrommodesdate
from utl.normalize import sphinxify

DEFAULT_EXHIBITION_PLACE = 'HRM'
PROD_SUMMARYTEXT = 'Production_SummaryText'
TITLE_FIRST_PUBLISHED = 'TitleFirstPublished'
NEEDS_CLEANING = False
REPLACE_FROM = ''
REPLACE_TO = ''


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def decade(datebegin, dateend):
    matbegin = re.match(r'.*(\d{4})$', datebegin)
    matend = re.match(r'.*(\d{4})$', dateend)
    dec = ''
    if matbegin:
        year = int(matbegin.group(1))
        decbegin = (year // 10) * 10
        if matend:
            year = int(matend.group(1))
            decend = (year // 10) * 10
        else:
            decend = decbegin
        dec = '|'.join([str(d) + 's' for d in range(decbegin, decend + 10, 10)])
    return dec


def clean(s):
    if NEEDS_CLEANING:
        s = s.replace(REPLACE_FROM, REPLACE_TO)
    return s


def onerow(oldrow):
    newrow = dict()
    newrow['Serial'] = oldrow['Serial']
    newrow['Title'] = clean(oldrow['Title'])
    newrow['Medium'] = oldrow['Medium']
    newrow['Description'] = clean(oldrow['Description'])
    # Append the Production/SummaryText field to the end of the
    # Description field unless it just repeats the same text.
    # If Production/SummaryText is empty, use the First Published In title.
    prod_text = oldrow[PROD_SUMMARYTEXT]
    if not prod_text and oldrow[TITLE_FIRST_PUBLISHED]:
        prod_text = f'First published in {oldrow[TITLE_FIRST_PUBLISHED]}'
    if prod_text:
        if newrow['Description']:
            if prod_text.lower() not in newrow['Description'].lower():
                newrow['Description'] += f' ({prod_text})'
        else:
            newrow['Description'] = prod_text

    datebegin = oldrow['DateBegin']
    dateend = oldrow['DateEnd']
    accuracy = oldrow['Accuracy']
    use_published_date = False
    if not datebegin or datebegin == 'unknown':
        if datebegin := oldrow['DateFirstPublished']:
            use_published_date = True
    if not datebegin:
        # Maybe it's a book, get the publication date
        datebegin = oldrow['Date']
    newrow['HumanDate'] = britishdatefrommodes(datebegin)
    if use_published_date:
        newrow['HumanDate'] += ' (Date Published)'
    if accuracy == 'circa':
        newrow['HumanDate'] = 'c. ' + newrow['HumanDate']
        if dateend:
            newrow['HumanDate'] += ' - ' + britishdatefrommodes(dateend)
    try:
        newrow['IsoDate'] = isoformatfrommodesdate(datebegin)
    except ValueError:
        newrow['IsoDate'] = ''
    newrow['Decade'] = decade(datebegin, dateend)

    places = oldrow['ExhibitionPlace'].split('|')
    names = oldrow['ExhibitionName'].split('|')
    if len(places) != len(names):
        print(f'Exhibition name/place mismatch count: {oldrow["Serial"]}')
        return None
    exhibitions = []
    for name, place in zip(names, places):
        if name.strip():
            # Note: exhibition.py will insert HRM as the exhibition place
            # if no place is explicitly given in cfg/exhibition_list.py
            if place == DEFAULT_EXHIBITION_PLACE:
                exhibitions.append(clean(name))
            else:
                exhibitions.append(f"{clean(name)} at {clean(place)}")
    newrow['Exhibition'] = '|'.join(exhibitions)

    if oldrow['ObjectType'] == 'books':
        newrow['Medium'] = 'book'
    elif oldrow['ObjectType'] != 'Original Artwork' and not newrow['Medium']:
        newrow['Medium'] = oldrow['ObjectType']
    return newrow


def main():
    global nrows
    reader = csv.DictReader(incsvfile)
    fields = 'Serial Title Medium Exhibition HumanDate IsoDate Decade'
    fields += ' Description'
    writer = csv.DictWriter(outfile, fieldnames=fields.split())
    writer.writeheader()
    nrows = 0
    for oldrow in reader:
        newrow = onerow(oldrow)
        if newrow:
            writer.writerow(newrow)
        nrows += 1


def getparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='''
    Read a CSV file, recode columns and write the CSV file. The Exhibition
    Name and Exhibition Place columns are merged into a "name at place" format
    unless the place is "HRM" in which case it's omitted.
    The DateBegin column (in Modes format) is deleted and replaced by a
    human-friendly column and an ISO date column.
    
    The input columns are defined in ``cfg/website.yml`` and must match
    names hard-coded here.''')
    parser.add_argument('incsvfile', help=sphinxify('''
        The input is expected to have been produced by xml2csv.py using the
        website.yml config file. You must specify the --heading option
        ''', called_from_sphinx))
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


called_from_sphinx = True


if __name__ == '__main__':
    global nrows
    assert sys.version_info >= (3, 9)
    called_from_sphinx = False
    _args = getargs(sys.argv)
    incsvfile = codecs.open(_args.incsvfile, 'r', encoding='utf-8-sig')
    outfile = codecs.open(_args.outfile, 'w', encoding='utf-8-sig')
    trace(1, 'Begin recode_collection.')
    trace(1, '    Input file: {}', _args.incsvfile)
    trace(1, '    Creating file: {}', _args.outfile)
    main()
    trace(1, 'End recode_collection. {} row{} written.', nrows,
          '' if nrows == 1 else 's')
