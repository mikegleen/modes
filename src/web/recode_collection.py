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
PAGE_FIRST_PUBLISHED = 'PageFirstPublished'
NEEDS_CLEANING = False
REPLACE_FROM = ''
REPLACE_TO = ''

WHR_YD = 1944  # Year WHR died

FIELDS = 'Serial Title Medium Exhibition HumanDate IsoDate Decade'
FIELDS += ' Description Height Width'


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def decade(datebegin, dateend):
    matbegin = re.match(r'.*(\d{4})$', datebegin)
    matend = re.match(r'.*(\d{4})$', dateend)
    dec = ''
    if matbegin:
        year = int(matbegin.group(1))
        if year > WHR_YD:  # probably a year first published
            return dec
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
    newrow['Serial'] = oldrow['Serial'].upper()  # to be sure to be sure
    newrow['Title'] = clean(oldrow['Title'])
    newrow['Medium'] = oldrow['Medium']
    newrow['Description'] = clean(oldrow['Description'])
    # Append the Production/SummaryText field to the end of the
    # Description field unless it just repeats the same text.
    # If Production/SummaryText is empty, use the First Published In title.
    # Append the page number from the First Published In element if the
    # Production/SummaryText or First-Published-In exists.
    from_tfp = False  # the text is from the title first published
    prod_text = oldrow[PROD_SUMMARYTEXT]
    page_text = oldrow[PAGE_FIRST_PUBLISHED]
    if not prod_text and oldrow[TITLE_FIRST_PUBLISHED]:
        prod_text = f'First published in {oldrow[TITLE_FIRST_PUBLISHED]}'
        from_tfp = True
    if prod_text:
        if newrow['Description']:
            if prod_text.lower() not in newrow['Description'].lower():
                newrow['Description'] += f' ({prod_text})'
        else:
            newrow['Description'] = prod_text
    if from_tfp and page_text:
        pg = ' page' if page_text.isdigit() else ''
        newrow['Description'] += f',{pg} {page_text}'

    # ------------------------- Dates ----------------------------------

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

    # ------------------------- Exhibitions ----------------------------------

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

    # ------------------------- ObjectType ----------------------------------

    if oldrow['ObjectType'] == 'books':
        newrow['Medium'] = 'book'
    elif oldrow['ObjectType'] != 'Original Artwork' and not newrow['Medium']:
        newrow['Medium'] = oldrow['ObjectType']

    # ------------------------- Dimensions ----------------------------------

    m = re.search(r'(\d+)\D+(\d+)', oldrow['Dimensions'])
    if m:
        newrow['Height'] = m.group(1) + ' mm'
        newrow['Width'] = m.group(2) + ' mm'
    # print(f'{oldrow["Dimensions"]=}, {newrow["Height"]=}, {newrow["Width"]=}')
    return newrow


def main():
    reader = csv.DictReader(incsvfile)
    n_input_fields = len(reader.fieldnames)
    writer = csv.DictWriter(outfile, fieldnames=FIELDS.split())
    writer.writeheader()
    n_rows = 0
    for oldrow in reader:
        if len(oldrow) > n_input_fields:
            print(f"Error: row {n_rows + 1} longer than heading: {oldrow}")
            return
        newrow = onerow(oldrow)
        if newrow:
            writer.writerow(newrow)
        n_rows += 1
    return n_rows


def getparser() -> argparse.ArgumentParser:
    """
    Called either by getargs() in this file or by Sphinx.
    :return: an argparse.ArgumentParser object
    """
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
    assert sys.version_info >= (3, 9)
    called_from_sphinx = False
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    incsvfile = codecs.open(_args.incsvfile, 'r', encoding='utf-8-sig')
    outfile = codecs.open(_args.outfile, 'w', encoding='utf-8-sig')
    trace(1, 'Begin recode_collection.')
    trace(1, '    Input file: {}', _args.incsvfile)
    trace(1, '    Creating file: {}', _args.outfile)
    nrows = main()
    trace(1, 'End recode_collection. {} row{} written.', nrows,
          '' if nrows == 1 else 's')
