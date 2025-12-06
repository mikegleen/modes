"""
    Rename files in a directory, prepending the containing directory name followed by "-".
    For directory names such as JB1201_2025-01-12, the text before the underscore is used.

    File names are of the form <item>[<face>] or <item>-page[<face>]
"""
import os.path
import re
import sys

DRYRUN = False


def rename(indir, oldfn, newfn):
    src = os.path.join(indir, oldfn)
    dst = os.path.join(indir, newfn)
    if not DRYRUN:
        os.rename(src, dst)


def getfiles(indir):
    if not os.path.isdir(indir):
        print('Parameter must be a directory name. Aborting with no action.')
        sys.exit(1)
    files = os.listdir(indir)
    if '.DS_Store' in files:
        files.remove('.DS_Store')
    return sorted(files)


def padfile(itemnum: str) -> str | None:
    # Note this pattern will fail if both face1 and face2 are present.
    m = re.fullmatch(r'''(\d+)  # item number
    ((?P<face1>A|B)  # front or back
    |(-(?P<pg>\d+) # page number
    (?P<face2>A|B)?  # front or back
    )?  # page + face
    )?  # everything after item''', itemnum, flags=re.IGNORECASE + re.VERBOSE)
    if not m:
        return None
    res = m[1].rjust(3, '0') + (m['face1'] if m['face1'] else '')
    if m['pg']:
        res += '-' + m['pg'].rjust(3, '0') + (m['face2'] if m['face2'] else '')
    return res.upper()


def main(indir):
    """
    For filenames like 123.jpg or 123A.jpg or 123-1.jpg or 123-1A.jpg, pad the item
    numbers and page numbers to 3 digits and prepend the basename of the folder.
    So:
    17-1A.jpg ->JB1201-17-001A.jpg
    134.jpg ->JB1201-134.jpg
    139B.jpg ->JB1201-139B.jpg

    :param indir:
    :return:
    """
    validexts = '.jpg .jpeg .png'.split()
    files = getfiles(indir)
    accession_num = os.path.basename(indir).split('_')[0].upper()
    prefix = accession_num + '-'
    print(f'{accession_num=}')
    for oldname in files:
        lead, ext = os.path.splitext(oldname)
        lead = lead.removeprefix(prefix)
        if ext.lower() not in validexts:
            print(f'Ignoring {oldname}; invalid extension')
            continue
        padded = padfile(lead)
        if padded:
            newname = accession_num + '-' + padded + ext
            print(f'Convert {oldname} to {newname}')
            rename(indir, oldname, newname)
        else:
            print(f'Cannot parse {oldname}. Ignored')


if __name__ == '__main__':
    assert sys.version_info >= (3, 10)
    main(sys.argv[1])
