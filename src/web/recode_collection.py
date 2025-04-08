"""
    Add a column to a CSV file with the decade an object was created based on
    the 'DateBegin' column which came from ./Production/Date/DateBegin.

    Merge the 'Exhibition Name' and 'Exhibition Place' columns producing a
    single column of "<name> at <place>".

    Input is the CSV file produced by xml2csv.py using website.yml
    Also input is a file produced by x053_list_pages.py containing
    gallery information.

    Output is a reformatted CSV file to feed to WordPress.
"""
import argparse
import codecs
import csv
import os
import re
import sys
from inspect import getframeinfo, stack

from colorama import Fore, Style

from utl.normalize import britishdatefrommodes, normalize_id, denormalize_id
from utl.normalize import isoformatfrommodesdate
from utl.normalize import sphinxify

DEFAULT_EXHIBITION_PLACE = 'HRM'
PROD_SUMMARYTEXT = 'Production_SummaryText'
TITLE_FIRST_PUBLISHED = 'TitleFirstPublished'
PAGE_FIRST_PUBLISHED = 'PageFirstPublished'
NEEDS_CLEANING = False
REPLACE_FROM = ''
REPLACE_TO = ''
NUM_GALLERY_ITEMS = 20
WHR_DD = 1949  # Last year of the decade in which WHR died

GALLERY_LIST = [f'Gallery{n:02}' for n in range(1, NUM_GALLERY_ITEMS + 1)]
FIELDS = 'Serial Title Medium Exhibition HumanDate IsoDate Decade'
FIELDS += ' Description Dimensions Order'
FIELDS += ' ' + ' '.join(GALLERY_LIST)


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if _args.verbose > 1:
            caller = getframeinfo(stack()[1][0])
            print(f'{os.path.basename(caller.filename)} line {caller.lineno}: ', end='')
        if color:
            if len(args) == 0:
                print(f'{color}{template}{Style.RESET_ALL}')
            else:
                print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            if len(args) == 0:
                print(template)
            else:
                print(template.format(*args))


def decade(datebegin, dateend):
    matbegin = re.match(r'.*(\d{4})$', datebegin)
    matend = re.match(r'.*(\d{4})$', dateend)
    dec = ''
    if matbegin:
        year = int(matbegin.group(1))
        if year > WHR_DD:  # probably a year first published
            return dec
        decbegin = (year // 10) * 10
        if matend:
            year = int(matend.group(1))
            decend = (year // 10) * 10
        else:
            decend = decbegin
        dec = '|'.join([str(d) + 's' for d in range(decbegin, decend + 10, 10)])
    trace(3, f'{datebegin=} {dateend=} {dec=}')
    return dec


def clean(s):
    if NEEDS_CLEANING:
        s = s.replace(REPLACE_FROM, REPLACE_TO)
    return s


def read_img_csv_file() -> dict[list]:
    img_dict = {}
    if not _args.imgcsvfile:
        trace(1, 'Warning: no images loaded.', color=Fore.YELLOW)
        return img_dict
    with codecs.open(_args.imgcsvfile, encoding='utf-8-sig') as imgcsvfile:
        reader = csv.reader(imgcsvfile)
        for row in reader:
            n_serial = normalize_id(row[0])
            img_dict[n_serial] = row[1].split('|')
    return img_dict


def onerow(oldrow):
    # print(f'Object Type="{oldrow['ObjectType']}"')
    # See the discussion in x053_list_pages.py for why we discard this row.
    if oldrow['ObjectType'] == 'object group':
        trace(1, 'Discarding object group: {}', oldrow['Serial'])
        return None
    newrow = {}
    n_serial = normalize_id(oldrow['Serial'])
    newrow['Serial'] = denormalize_id(n_serial)  # to be sure to be sure
    trace(3, 'Serial = {}', newrow['Serial'])
    newrow['Title'] = clean(oldrow['Title'])
    newrow['Medium'] = oldrow['Medium']

    # ------------------------- Order ----------------------------------

    order = oldrow['Order']
    if not order.isnumeric() or not (1 <= int(order) <= 9):
        order = '9'
        trace(1, 'Serial = {}, order is not in range 1-9: {}, '
                 '"9" assigned.', newrow['Serial'], order, color=Fore.YELLOW)
    # Append the normalized accession number so that within a priority, images
    # are displayed in accession number order.
    newrow['Order'] = f'{order}_{n_serial}'

    # ------------------------- Description ------------------------------

    description = clean(oldrow['Description'])
    # Append the Production/SummaryText field to the end of the
    # Description field unless it just repeats the same text.
    # If Production/SummaryText is empty, use the First Published In title.
    # Append the page number from the First Published In element if the
    # Production/SummaryText or First-Published-In exists.
    # from_tfp = False  # the text is from the title first published
    prod_text = oldrow[PROD_SUMMARYTEXT]
    page_text = oldrow[PAGE_FIRST_PUBLISHED]
    if not prod_text and oldrow[TITLE_FIRST_PUBLISHED]:
        prod_text = f'First published in {oldrow[TITLE_FIRST_PUBLISHED]}'
        # from_tfp = True
        # page_text could be an actual page number or something like
        # "frontispiece". So only insert "page" if required.
        if page_text:
            pg = 'page' if page_text.isdigit() else ''
            prod_text += f', {pg} {page_text}'
    if prod_text:
        if description:
            if prod_text.lower() not in description.lower():
                description += f' ({prod_text})'
        else:
            description = prod_text
    # if from_tfp and page_text:
    #     pg = ' page' if page_text.isdigit() else ''
    #     description += f',{pg} {page_text}'

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
    trace(3, f'{newrow["Decade"]=}')

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

    # ------------------------- Dimensions ----------------------------------

    # The field is like "300 x 500" as height x width in mm.
    m = re.search(r'(\d+)\D+(\d+)', oldrow['Dimensions'])
    newrow['Dimensions'] = ''
    if m:
        height = m.group(1) + 'mm'
        width = m.group(2) + 'mm'
        # newrow['Height'] = height
        # newrow['Width'] = width
        newrow['Dimensions'] = f'Width: {width}<br/>Height: {height}'
        # print(f'{oldrow["Dimensions"]=}, {newrow["Height"]=}, {newrow["Width"]=}')
    if oldrow['Pages']:
        nl = '<br/>' if m else ''
        newrow['Dimensions'] += f"{nl}Number of Pages:{oldrow['Pages']}"

    # ------------------------- Gallery -------------------------------------

    if n_serial in imgdict:
        imglist = imgdict[n_serial]
        if len(imglist) > len(GALLERY_LIST):
            trace(1, '{} images exceed available columns.', n_serial,
                  color=Fore.YELLOW)
        gallery = zip(GALLERY_LIST, imglist)
        for key, value in gallery:
            newrow[key] = value
        del imgdict[n_serial]
    elif _args.imgcsvfile:
        trace(1, 'Cannot find images for {}', n_serial,
              color=Fore.YELLOW)

    # ------------------------- ObjectType ----------------------------------

    description = [description] if description else []
    if oldrow['ObjectType'] == 'letter':
        newrow['Medium'] = 'letter'
        if oldrow['Sender']:
            # if description:
            #     description.append('<br/>')
            description.append(f'Sender: {oldrow["Sender"]}')
        if oldrow['Sender Org']:
            # print(f'{n_serial=} "{oldrow["Sender Org"]=}", {description=}')
            # if description:
            #     description.append('<br/>')
            description.append(f'Sender Organisation: {oldrow["Sender Org"]}')
            # print(f'after append {description=}')
        if oldrow['Recipient']:
            # if description:
            #     description.append('<br/>')
            description.append(f'Recipient: {oldrow["Recipient"]}')
        if oldrow['Recipient Org']:
            # if description:
            #     description.append('<br/>')
            description.append(f'Recipient Organisation: {oldrow["Recipient Org"]}')
        # print(f'done {description=}')
    elif oldrow['ObjectType'] == 'cutting':
        newrow['Medium'] = 'cutting'
        if oldrow['Publ Name']:
            description.append(f'Publication: {oldrow["Publ Name"]}')

    elif oldrow['ObjectType'] == 'ephemera':
        newrow['Medium'] = 'ephemera'

    elif oldrow['ObjectType'] != 'Original Artwork' and not newrow['Medium']:
        newrow['Medium'] = oldrow['ObjectType']

    newrow['Description'] = '<br />'.join(description)
    return newrow


def main():
    inreader = csv.DictReader(incsvfile)
    n_input_fields = len(inreader.fieldnames)
    readers = [inreader]
    if _args.addendum:
        addreader = csv.DictReader(addendum)
        readers.append(addreader)
        if inreader.fieldnames != addreader.fieldnames:
            raise TypeError(f'Mismatch:\n{inreader.fieldnames=}\n{addreader.fieldnames=}')

    writer = csv.DictWriter(outfile, fieldnames=FIELDS.split())
    writer.writeheader()
    n_rows = 0
    for reader in readers:
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
    Read a CSV file, recode columns and write the CSV file.
    The Exhibition
    Name and Exhibition Place columns are merged into a "name at place" format
    unless the place is "HRM" in which case it's omitted.
    
    The DateBegin column (in Modes format) is deleted and replaced by a
    human-friendly column and an ISO date column.
    
    The Height, Width, and Pages columns are merged into a Dimensions column
    if present.
    
    The input columns are defined in ``cfg/website.yml`` and must match
    names hard-coded here.''')
    parser.add_argument('-i', '--incsvfile', help=sphinxify('''
        The input is expected to have been produced by ``xml2csv.py`` using the
        ``website.yml`` config file. You must specify the --heading option
        ''', called_from_sphinx))
    parser.add_argument('-a', '--addendum', help='''
        An extra manually created CSV file in the same format as the main input CSV file.
        This is used in case we want to upload an image that is not contained in Modes.''')
    parser.add_argument('-o', '--outfile', help='''
        The output CSV file.''')
    parser.add_argument('-g', '--imgcsvfile', required=False,
                        help=sphinxify('''
        This file contains two columns, the Serial number and a vertial bar
        separated list of image files. This file is created by ``x053_list_pages.py``.       
        ''', called_from_sphinx))
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
    incsvfile = codecs.open(_args.incsvfile, encoding='utf-8-sig')
    outfile = codecs.open(_args.outfile, 'w', encoding='utf-8-sig')
    trace(1, 'Begin recode_collection.', color=Fore.GREEN)
    trace(1, '    Input file: {}', _args.incsvfile)
    addendum = None
    if _args.addendum:
        addendum = codecs.open(_args.addendum, encoding='utf-8-sig')
        trace(1, '    Input addendum file: {}', _args.addendum)
    trace(1, '    Creating file: {}', _args.outfile)
    imgdict = read_img_csv_file()
    nrows = main()
    if len(imgdict):
        trace(1, '{} images discarded', len(imgdict))
    for serial in imgdict.keys():
        trace(2, '{}: images not used.', denormalize_id(str(serial)))
    trace(1, 'End recode_collection. {} row{} written.', nrows,
          '' if nrows == 1 else 's', color=Fore.GREEN)
