"""
    Create a CSV file where the first column is the accession number optionally including
    a sub-number and the second column is a list of filenames of images of
    the object. For example, the images could be of pages of a letter. The list
    is separated by a "|" character.

    Input is a folder containing image files and/or subfolders (to any level).

    The format of the filename is as follows:

    <accession #>-[[<3-digit subnumber>][<A|B>]][[-<page #>][<A|B>]]

    The accession number is mandatory. There can be one or more subnumbers.
    If there is a subnumber then it can have an "A" or "B" suffix indicating
    that there is a front and back image. Each subnumber can have multiple
    pages (i.e. sheets) each of which can have a front and back image.

    You can also have multiple pages associated with an accession number that
    doesn't have subnumbers. In this case the subnumber field will be empty
    resulting in a filename like "JB001--1A" with the 1A indicating a page number.

    You can have a single file for an object with a name corresponding to its
    accession number or you can have one or more files in the format of
    <accnum>-<subnum>[-<pagenum>] but you cannot mix the two formats.
    Here we keep track of files with the simple name so if we try to add
    a long-named file to the list it's an error. We also check when adding
    a simple-name file that there aren't already long-name files in the list.

    In the case where a subnumber exists, we do not know whether each subnumber
    has its own Modes Object element group or whether it is an Item group under
    a single Object for that accession number. Therefore we output a row for
    the accession number and a separate row for each subnumber. The output of
    this script is input to recode_collection.py which will read the Modes data
    and determine which row or rows to use.

    The output of this script is input to recode_collection.py.

    Note: This script doesn't completely check for valid file names. However,
    an invalid filename will generate an invalid accession number that will not
    be found in Modes.
"""
import argparse
import os
import sys
from collections import defaultdict
from colorama import Fore, Style

from utl.normalize import normalize_id, denormalize_id
from web.webutil import COLLECTION_PREFIX, parse_prefix

IMGFILES = ('.jpg', '.jpeg', '.png')


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
        denormed_filename = f'{parta}{"-" if partb else ""}{partb}'
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
    there is an Object element group in the XML file for the sub-number. These will
    be with an elementtype of "object group"

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
    if not prefix.startswith(COLLECTION_PREFIX) and not _args.force:
        print(f'File "{filename}" doesn’t start with {COLLECTION_PREFIX}. Ignored.')
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
    if n_modes_key2:  # if the filename includes a subnumber
        accndict[n_modes_key2].append(padded_filename)
    else:
        accndict[n_modes_key1].append(padded_filename)


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


def getparser():  # called either by getargs or sphinx
    parser = argparse.ArgumentParser(description='''
    Read the folder holding images and create a CSV file of accession number
    and filename(s).
        ''')
    parser.add_argument('indir', help='''
        The folder containing the images.''')
    parser.add_argument('outfile',  help='''
        The output CSV file.''')
    parser.add_argument('-f', '--force', action='store_true', help=f'''
        process a file even if the collection prefix "{COLLECTION_PREFIX}"
        is not specified,''')
    parser.add_argument('-m', '--mode', choices=('item', 'subnum'),
                        default='subnum',
                        help='''If the mode is "item", pictures will be grouped
                        under the accession number. If the mode is "subnum"
                        each subnumber is assumed to have its own Modes Object
                        element group. This means that you will be unable to
                        mix the two different modes in a single batch.''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    print(Fore.LIGHTGREEN_EX + 'Begin x053_list_pages.' + Style.RESET_ALL)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    num_failed_match = 0
    accndict = defaultdict(list)
    inputdir = _args.indir
    outfile = open(_args.outfile, 'w')
    main(inputdir)
    print(f'Creating file: {outfile.name}')
    print(Fore.LIGHTGREEN_EX + 'End x053_list_pages.' + Style.RESET_ALL)
