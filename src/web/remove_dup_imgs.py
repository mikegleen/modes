"""
Delete every file in a directory and its subdirectories if it is a duplicate
in that tree.

Directories are processed in alphabetical order.

"""
import argparse
import os.path
import re
import sys
from utl.normalize import normalize_id


def trace(level, template, *args):
    if VERBOSE >= level:
        print(template.format(*args))


def getargs():
    parser = argparse.ArgumentParser(description='''
    Delete every file in a directory and its subdirectories if it is a duplicate
    in that tree.

    Directories are processed in alphabetical order.
    ''')
    parser.add_argument('imgdir', help='''
        Folder containing images or subfolders containing images we already
        have.''')
    parser.add_argument('--delete', action='store_true', help='''
        Delete the duplicate files. Otherise, print but do not delete files.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


def handle_folder(img_ids: dict, imgdir: str):
    """
    Build a set of normalized accession numbers from the folders containing
    images.
    :return: The set of normalized numbers.
    """
    def onefile(imgf: str):
        m = re.match(r'(collection_)?(.*)', imgf)
        imgf2 = m.group(2)  # remove optional leading 'collection_'
        prefix, suffix = os.path.splitext(imgf2)
        if suffix.lower() not in ('.jpg', '.png'):
            if _args.verbose > 1:
                print('not image:', imgf)
            return
        try:
            nid = normalize_id(prefix)
        except ValueError as ve:
            print(f'Skipping {imgf}')
            return
        if nid in img_ids:
            print(f'Duplicate: {prefix} in {dirpath.removeprefix(_args.imgdir)},'
                  f'original in {img_ids[nid][0].removeprefix(_args.imgdir)}')
            if  _args.delete:
                print(f'Removing {dirpath}')
                os.remove(dirpath)
        else:
            print(f'Added: {imgf}')
            img_ids[nid] = (dirpath, imgf)

    for subfile in sorted(os.listdir(imgdir)):
        dirpath = os.path.join(imgdir, subfile)
        if os.path.isdir(dirpath):
            trace(1, 'Folder {}', dirpath)
            handle_folder(img_ids, dirpath)
        else:
            onefile(subfile)
            continue
    return img_ids


def main():
    # x.normalized extracts the first entry in the namedtuple Obj_id.

    img_ids = dict()
    handle_folder(img_ids, _args.imgdir)
    trace(1, '{} image files found.', len(img_ids))


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    _args = getargs()
    if not os.path.isdir(_args.imgdir):
        raise ValueError(f'{_args.imgdir} is not a directory.')
    if _args.verbose < 2:
        sys.tracebacklimit = 0
    VERBOSE = _args.verbose
    main()
