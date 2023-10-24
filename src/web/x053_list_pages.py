"""
    Create a CSV file where the first column is the accession number including
    a sub-number and the second column is a list of filenames of images of
    the object. For example, the images could be of pages of a letter. The list
    is separated by a "|" character.

    Input is a folder containing sub-folders, each of which contains images.

    This script is copied from x051 and handles a folder containing image files
    and/or subfolders (to any level).

    The output of this script is input to recode_collection.py.

    You can have single file for an object with a name corresponding to its
    accession number or you can have one or more files in the format of
    <accnum>-<subnum>[-<pagenum>] but you cannot mix the two formats.
    Here we keep track of files with the simple name so if we try to add
    a long-named file to the list it's an error. We also check when adding
    a simple-name file that there aren't already long-name files in the list.
"""
import os
import re
import sys
from collections import defaultdict

from utl.normalize import normalize_id, denormalize_id

#
#   <accession #>-<3-digit subnumber>[<A|B>][-<page #>][<A|B>]
#   The 'A|B' can either follow the subnumber or the page number (or neither)
#   but not both. This is not enforced by the pattern.
#
FILENAMEPAT = r'(.+?)-(\d{3})([AB]?)(-(\d+)([AB])?)?$'

"""
'JB2-003-2B'
Groups:   1      2     3    4     5    6
       ('JB2', '003', '', '-2B', '2', 'B'
"""

IMGFILES = ('.jpg', '.jpeg', '.png')
COLLECTION_PREFIX = 'collection_'


def normalize_filename(filename: str, suffix: str, m: re.Match):
    # Pad the page number to three digits
    # print(f'{filename=}')
    if m is None:
        return filename
    parta = f'{m.group(1)}-{m.group(2)}'

    if m.group(5):  # if a page number exists
        page = f'{int(m.group(5)):03}'
        if m.group(6):
            page += m.group(6)
        nfilename = f'{parta}-{page}{suffix}'
        # print(f'{filename=}, {nfilename=}')
        return nfilename
    else:
        return filename


def denormalize_filename(filename):
    # Remove the padding from the page number.
    prefix, suffix = os.path.splitext(filename)
    m = re.match(FILENAMEPAT, prefix)
    if m is None:
        return denormalize_id(prefix) + suffix
    if m.group(5):
        parta = f'{m.group(1)}-{m.group(2)}'
        page = f'{int(m.group(5))}'
        if m.group(6):
            page += m.group(6)
        return f'{parta}-{page}{suffix}'
    else:
        return filename


def one_file(filename):
    """
    Extract the accession number from the filename and update the global dict
    with the key as the accession number of an object and the value the list of
    its files.
    :param filename: filename in the format of an accession number or FILENAMEPAT
    :return: None
    """

    global num_failed_match
    m = None
    prefix, suffix = os.path.splitext(filename)
    if suffix.lower() not in IMGFILES:
        if filename != '.DS_Store':
            print(f'Skipping not image: {filename}')
        return
    try:
        # fails if the name contains a page number
        naccn = normalize_id(prefix.removeprefix(COLLECTION_PREFIX))
    except ValueError:
        m = re.match(FILENAMEPAT, prefix)
        if not m:
            print(f'Filename failed match: {filename}')
            num_failed_match += 1
            return
        if m.group(3) and m.group(4):
            raise ValueError(f'Illegal filename format: {filename}, cannot'
                             f' have A/B token before the page number.')
        accn = f'{m.group(1)}.{int(m.group(2))}'
        naccn = normalize_id(accn.removeprefix(COLLECTION_PREFIX))
    accndict[naccn].append(normalize_filename(filename, suffix, m))


def main(indir):
    for file in os.listdir(indir):
        filepath = os.path.join(indir, file)
        if os.path.isdir(filepath):
            main(filepath)
        else:
            one_file(file)

    listlen = 0
    longest = None
    for accn, filelist in sorted(accndict.items()):
        if len(filelist) > listlen:
            listlen = len(filelist)
            longest = accn
        filelist.sort()
        denormed_filelist = [denormalize_filename(filename) for filename in filelist]
        files = '|'.join(denormed_filelist)
        print(f'{denormalize_id(accn)},{files}', file=outfile)
    print(f'Longest page list: {denormalize_id(longest)}, length: {listlen}')
    print(f'Number failed match: {num_failed_match}')


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    num_failed_match = 0
    accndict = defaultdict(list)
    # singlefile = set()
    inputdir = sys.argv[1]
    outfile = open(sys.argv[2], 'w')
    main(inputdir)
