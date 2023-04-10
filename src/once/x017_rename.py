"""
    Rename files in a directory: JBxxx_title.jpg -> JBxxx.jpg
"""
import os.path
import re
import sys


def rename1():
    """
        Rename files in a directory: JBxxx_title.jpg -> JBxxx.jpg
    """
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


def rename_scanned(title):
    """
    VueScan creates files in the form yyyy-mm-dd-nnnn.
    Convert names of page scans of a book to recto-verso
    :return:
    """
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


if __name__ == '__main__':
    assert sys.version_info >= (3, 10)
    indir = sys.argv[1]
    files = os.listdir(indir)
    rename_scanned('lets_laugh')
