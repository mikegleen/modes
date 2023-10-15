"""
    Create a CSV file where the first column is the accession number including
    a sub-number and the second column is a list of filenames of images of
    the object. For example, the images could be of pages of a letter. The list
    is separated by a "|" character.

    Input is a folder containing sub-folders, each of which contains images.
"""
import os
import re
import sys
from collections import defaultdict

from utl.normalize import normalize_id, denormalize_id

FILENAMEPAT = r'(.+?)-(\d{3})[AB]?(-(\d+)([AB])?)?$'

"""
'JB2-003-2B'
('JB2', '003', '-2B', '2', 'B')
"""


def normalize_filename(filename: str, suffix: str, m: re.Match):
    # Pad the page number to three digits
    parta = f'{m.group(1)}-{m.group(2)}'

    if m.group(4):  # if a page number exists
        page = f'{int(m.group(4)):03}'
        if m.group(5):
            page += m.group(5)
        return f'{parta}-{page}{suffix}'
    else:
        return filename


def denormalize_filename(filename):
    # Remove the padding from the page number.
    prefix, suffix = os.path.splitext(filename)
    m = re.match(FILENAMEPAT, prefix)
    if m.group(4):
        parta = f'{m.group(1)}-{m.group(2)}'
        page = f'{int(m.group(4))}'
        if m.group(5):
            page += m.group(5)
        return f'{parta}-{page}{suffix}'
    else:
        return filename


def one_subdir(subdirpath):
    global num_failed_match
    for filename in os.listdir(subdirpath):
        prefix, suffix = os.path.splitext(filename)
        if suffix.lower() not in ('.jpg', '.jpeg'):
            if filename != '.DS_Store':
                print(f'Skipping not image: {filename}')
            continue
        m = re.match(FILENAMEPAT, prefix)
        if not m:
            print(f'Filename failed match: {filename}')
            num_failed_match += 1
            continue
        accn = f'{m.group(1)}.{int(m.group(2))}'
        accndict[normalize_id(accn)].append(normalize_filename(filename, suffix, m))


def main():
    indir = sys.argv[1]
    for subdir in os.listdir(indir):
        subdirpath = os.path.join(indir, subdir)
        if not os.path.isdir(subdirpath):
            if subdir != '.DS_Store':
                print(f'Skipping not folder: {subdir}')
            continue
        one_subdir(subdirpath)
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
    outfile = open(sys.argv[2], 'w')
    main()
