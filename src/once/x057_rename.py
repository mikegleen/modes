"""
    Rename files in a directory, prepending the containing directory name followed by "-".
    For directory names such as JB1201_2025-01-12, the text before the underscore is used.

    File names are of the form <item>[<face>] or <item>-page[<face>]
"""
import os.path
import re
import sys


def rename(indir, oldfn, newfn):
    src = os.path.join(indir, oldfn)
    dst = os.path.join(indir, newfn)
    # print(f'{src=}, {dst=}')
    os.rename(src, dst)


def getfiles(indir):
    if not os.path.isdir(indir):
        print('Parameter must be a directory name. Aborting with no action.')
        sys.exit(1)
    files = os.listdir(indir)
    if '.DS_Store' in files:
        files.remove('.DS_Store')
    return files


def rename1(indir):
    """
        Rename files in a directory: JBxxx_title.jpg -> JBxxx.jpg
    """
    files = getfiles(indir)
    for fn in files:
        # if '_' not in fn or not fn.lower().endswith('.jpg'):
        #     print(f'filename doesn\'t parse: {fn}')
        #     continue
        # prefix = fn.split('_')[0]
        prefix, ext = os.path.splitext(fn)
        prefix = prefix.replace('LDHRM2019', 'LDHRM.2019')
        src = os.path.join(indir, fn)
        dst = os.path.join(indir, prefix + ext)
        print(f'\n{src}\n{dst}')
        os.rename(src, dst)


def rename_scanned(indir, title):
    """
    VueScan creates files in the form yyyy-mm-dd-nnnn.
    Convert names of page scans of a book to recto-verso
    :return:
    """
    files = getfiles(indir)
    for fn in files:
        m = re.match(r'.*-(\d{4})', fn)
        if not m:
            print(f'{fn} skipped.')
            continue
        n = int(m.group(1))
        p2 = (p1 := 2 * n - 2) + 1
        src = os.path.join(indir, fn)
        dst = os.path.join(indir, f'{title}_{p1:03}-{p2:03}')
        # print(src, dst)
        os.rename(src, dst)


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
    accession_num = os.path.basename(indir).split('_')[0]
    print(f'{accession_num=}')
    for oldname in files:
        lead, ext = os.path.splitext(oldname)
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


def main2(indir):
    """
    For filenames like JB1201-nnn[AB]-m[AB], right justify the page number (m) padding with
    zeros.

    :param indir:
    :return:
    """
    prefix = 'JB1201-'
    validexts = '.jpg .jpeg .png'.split()
    files = getfiles(indir)
    for fn in files:
        # print(f'{fn=}')
        lead, ext = os.path.splitext(fn)
        if ext.lower() not in validexts:
            print(f'Ignoring {fn}.')
            continue
        if (trimmed := lead.removeprefix(prefix)) == lead:
            print(f'Failed match for {prefix}: {fn}, ignored.')
            continue
        padded = padfile(trimmed)
        if padded:
            final = prefix + padded + ext
            print(f'{fn} ->{final}')
            rename(indir, fn, final)
        else:
            print(f'Cannot parse {fn}. Ignored')


if __name__ == '__main__':
    assert sys.version_info >= (3, 10)
    main(sys.argv[1])
