"""
List every file in a directory and its subdirectories marking any that are
duplicates in that tree.

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


def getparser():
    parser = argparse.ArgumentParser(description='''
    List every file in a directory and its subdirectories marking any that are
    duplicates in that tree.

    Directories are processed in alphabetical order.
    ''')
    parser.add_argument('imgdir', help='''
        Folder containing images or subfolders containing images we already
        have.''')
    parser.add_argument('-o', '--outfile', help='''
        Output file for the list of files. Default is sys.stdout. The warning
        messages are always written to sys.stdout.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
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
        else:
            img_ids[nid] = (imgf2, dirpath)

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
    img_ids = dict()
    handle_folder(img_ids, _args.imgdir)
    for key in sorted(img_ids.keys()):
        fname = img_ids[key][0]
        prefix, _ = os.path.splitext(fname)
        print(f'{prefix},{img_ids[key][1]}', file=outfile)
    trace(2, '{} image files found.', len(img_ids))


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    _args = getargs(sys.argv)
    if not os.path.isdir(_args.imgdir):
        raise ValueError(f'{_args.imgdir} is not a directory.')
    if _args.verbose < 2:
        sys.tracebacklimit = 0
    VERBOSE = _args.verbose
    if _args.outfile:
        outfile = open(_args.outfile, 'w')
    else:
        outfile = sys.stdout
    main()
