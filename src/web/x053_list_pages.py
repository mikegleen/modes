"""
    Create a CSV file where the first column is the accession number including
    a sub-number and the second column is a list of filenames of images of
    the object. For example, the images could be of pages of a letter. The list
    is separated by a "|" character.

    Input is a folder containing image files and/or subfolders (to any level).

    You can have single file for an object with a name corresponding to its
    accession number or you can have one or more files in the format of
    <accnum>-<subnum>[-<pagenum>] but you cannot mix the two formats.
    Here we keep track of files with the simple name so if we try to add
    a long-named file to the list it's an error. We also check when adding
    a simple-name file that there aren't already long-name files in the list.

    The output of this script is input to recode_collection.py.

    Note: This script doesn't completely check for valid file names. However,
    an invalid filename will generate an invalid accession number that will not
    be found in Modes.
"""
import os
import re
import sys
from collections import defaultdict
from colorama import Fore, Style

from utl.normalize import normalize_id, denormalize_id

#
#   <accession #>-<3-digit subnumber>[<A|B>][-<page #>][<A|B>]
#   The 'A|B' can either follow the subnumber or the page number (or neither)
#   but not both. This is not enforced by the pattern.
#
FILENAMEPAT = (r'^(?P<accn>[^\-]*)'
               r'(-((?P<subn>\d{3})(?P<subnAB>[A-Z])?(-(?P<page>\d+)(?P<pageAB>[A-Z])?)?))?')
#                1 23             33              3 3 4           44              4 3 21
"""
'JB001-001-3A'
Groups:   1        2       3     4      5     6    7
       ('JB001', '-001', '001', None, '-3A', '3', 'A')
"""
#
# FILENAMEPAT2 is for the case where there is "--" in the filename indicating
# that this is an accession number without subnumbers but with page numbers.
#
FILENAMEPAT2 = (r'^(?P<accn>[^\-]*)'
                r'--((?P<page>\d+)(?P<pageAB>[A-Z])?)')
#                   12           22              2 1

IMGFILES = ('.jpg', '.jpeg', '.png')
COLLECTION_PREFIX = 'collection_'


def parse_prefix(prefix):
    prefix = prefix.removeprefix(COLLECTION_PREFIX)
    if '--' in prefix:
        # There is no subnum but there is a page number.
        m = re.match(FILENAMEPAT2, prefix)
        if not m:
            raise ValueError(f'File prefix failed match (FILENAMEPAT2): {prefix}')
        accn = m['accn']
        subn = subn_ab = ''
        page = m['page']
        page_ab = m['pageAB'] if m['pageAB'] else ''
        modes_key1 = accn
        modes_key2 = None
    else:
        m = re.match(FILENAMEPAT, prefix)
        if not m:
            raise ValueError(f'File prefix failed match (FILENAMEPAT): {prefix}')
        accn = m['accn']
        modes_key1 = accn
        if m['subn']:
            subn = m["subn"]
            subn_ab = m['subnAB'] if m['subnAB'] else ''
            modes_key2 = f'{accn}.{int(subn)}'
            page = m['page'] if m['page'] else ''
            page_ab = m['pageAB'] if m['pageAB'] else ''
        else:
            subn = subn_ab = page = page_ab = ''
            modes_key2 = None
    return accn, subn, subn_ab, page, page_ab, modes_key1, modes_key2


def pad_page_number(prefix, suffix, accn, subnum, subnum_ab, pagenum, pagenum_ab):
    # Pad the page number to three digits
    # print(f'{filename=}')

    if pagenum:  # if a page number exists
        parta = f'{accn}-{subnum}{subnum_ab}'
        page = f'{int(pagenum):03}{pagenum_ab}'
        nfilename = f'{parta}-{page}{suffix}'
        # print(f'{filename=}, {nfilename=}')
        return nfilename
    else:
        return prefix + suffix


def unpad_page_number(filename: str):
    # Remove the padding from the page number.
    filename = filename.removeprefix(COLLECTION_PREFIX)
    prefix, suffix = os.path.splitext(filename)
    # parse_prefix has already been called once so it shouldn't raise an exception
    (accn, subn, subn_ab, page, page_ab, modes_key1,
     modes_key2) = parse_prefix(prefix)

    if subn or page:
        parta = f'{accn}-{subn}{subn_ab}'
        partb = f'{int(page)}{page_ab}' if page else ''
        denormed_filename = f'{parta}-{partb}'
    else:
        denormed_filename = accn  # simple accession number
    return COLLECTION_PREFIX + denormed_filename + suffix


def one_file(filename):
    """
    Extract the accession number with or without a subnumber from the filename and update `accndict`
    with the key as the accession number of an object and the value as the list of
    its files. The filename is normalized so that the page number is three digits
    so that it sorts correctly.

    There are two cases of accession number. It can be a main number such as
    "JB001" or a main number with a sub-number such as "JB001.2". In some cases
    there is an Object element group in the XML file for the sub-number and in
    other cases the sub-number is an Item under a main number. We cannot tell
    which cases it is from the filename so we insert both cases into accndict
    only one of which will be found in the XML file.

    :param filename: filename in one of the following formats:

        JB001.jpg
        JB001-001[A].jpg
        JB001-001-1[A].jpg
        JB001--1[A].jpg

        JB001   The accession number
        -001    The subnumber
        A       The page indicator can be A (verso) or B (recto)
        --      Indicates that an object with an accession number but not a
                subnumber has multiple pages

    :return: None
    """

    global num_failed_match
    prefix, suffix = os.path.splitext(filename)
    if suffix.lower() not in IMGFILES:
        if filename != '.DS_Store':  # MacOS magic file
            print(f'Skipping not image: {filename}')
        return
    if not prefix.startswith(COLLECTION_PREFIX):
        print(f'File "{filename}" doesn’t strt with {COLLECTION_PREFIX}. Ignored.')
        return
    try:
        accn, subn, subn_ab, page, page_ab, modes_key1, modes_key2 = parse_prefix(prefix)
    except ValueError:
        print(f'Filename failed match: {filename}')
        num_failed_match += 1
        return
    n_modes_key1 = normalize_id(modes_key1)
    n_modes_key2 = normalize_id(modes_key2)
    # Pad the page number in the filename so the pages are sorted so they appear
    # on the website in order.
    padded_filename = pad_page_number(prefix, suffix, accn, subn, subn_ab, page, page_ab)
    accndict[n_modes_key1].append(padded_filename)
    if n_modes_key2:  # if the filename includes a subnumber
        accndict[n_modes_key2].append(padded_filename)


def main(indir):
    #
    #   Create accndict containing accn --> list of files
    #
    for file in os.listdir(indir):
        filepath = os.path.join(indir, file)
        if os.path.isdir(filepath):
            main(filepath)  # recursively walk subdirectory
        else:
            one_file(file)

    listlen = 0
    longest = None
    for accn, filelist in sorted(accndict.items()):
        if len(filelist) > listlen:
            listlen = len(filelist)
            longest = accn
        filelist.sort()
        # Now return the filenames to the unpadded form, that is, as they
        # actually appear in the folder.
        unpadded_filelist = [unpad_page_number(filename) for filename in filelist]
        files = '|'.join(unpadded_filelist)
        print(f'{denormalize_id(accn)},{files}', file=outfile)
    print(f'Longest page list: {denormalize_id(longest)}, length: {listlen}')
    print(f'Number failed match: {num_failed_match}')


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    print(Fore.LIGHTGREEN_EX + 'Begin x053_list_pages.' + Style.RESET_ALL)
    num_failed_match = 0
    accndict = defaultdict(list)
    inputdir = sys.argv[1]
    outfile = open(sys.argv[2], 'w')
    main(inputdir)
    print(Fore.LIGHTGREEN_EX + 'End x053_list_pages.' + Style.RESET_ALL)
