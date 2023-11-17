"""
    Read a directory of JPEG files and create a CSV file with one column
    containing the filename minus the trailing .jpg
    A heading row of 'Serial' precedes the data.
"""
import argparse
import os.path
import re
import sys
from utl.normalize import normalize_id, denormalize_id


def _onedir(ld, subdirname: str):
    fnpat = r'(\w+)-(\d{3}).*\.(jpg|jpeg)'
    for fn in os.listdir(os.path.join(_args.indir, subdirname)):
        m = re.match(fnpat, fn)
        if m:
            an = m.group(1)  # accession #
            seq = m.group(2)
            if fn in ld[(an, seq)]:
                print(f'Duplicate filename {fn}')
            ld[(an, seq)].add(fn)
        elif fn != '.DS_Store':
            print(f'Ignored: {subdirname}/{fn}')


def dir2listsub(jpegdir):
    fnpat = r'(collection_)?(\w+)-(\d{3}).*\.(jpg|jpeg)'
    jpgset = set()
    jpgfiles = os.listdir(jpegdir)
    for jpgfile in jpgfiles:
        m = re.match(fnpat, jpgfile)
        if not m:
            print(f'dir2list skipping: {jpgfile}')
            continue
        accn = f'{m[2]}.{m[3]}'
        try:
            accn = normalize_id(accn, verbose=2)
        except ValueError:
            pass
        jpgset.add(accn)
    return sorted(list(jpgset))


def dir2list(jpegdir):
    jpglist = list()
    jpgfiles = os.listdir(jpegdir)
    for jpgfile in jpgfiles:
        m = re.match(r'(collection_)?(.+)\.jpg', jpgfile)
        if not m:
            print(f'dir2list skipping: {jpgfile}')
            continue
        accn = m[2]
        try:
            accn = normalize_id(accn, verbose=2)
        except ValueError:
            pass
        jpglist.append(accn)
    return sorted(jpglist)


def getparser():
    parser = argparse.ArgumentParser(description='''
        For every JPG file in a directory write the name minus the trailing
        ".jpg" to a CSV file.
        ''')
    parser.add_argument('indir', help='''
        Folder containing images to list''')
    parser.add_argument('csvfile', help='''
        Output CSV file containing the accession numbers extracted from the filenames
        in indir''')
    parser.add_argument('-n', '--normalize', action='store_true', help='''
        Noramlize the accession number written to the CSV file.
        ''')
    parser.add_argument('-s', '--subnumber', action='store_true', help='''
        The filenames include a 3-digit sub-number following a '-', possibly
        followed by another '-' and a page number. The subnumber has leading
        zeros removed and appended to the accession number following a full stop.
        Trailing page numbers are discarded. If multiple pages are found for a
        single object, only one row is written to the CSV file.
        ''')
    parser.add_argument('--heading', action='store_true', help='''
        Write a row at the front of the CSV file containing 'Serial'.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    indir = _args.indir
    outfile = open(_args.csvfile, 'w')

    if _args.subnumber:
        outlist = dir2listsub(indir)
    else:
        outlist = dir2list(indir)
    nout = 0
    if _args.heading:
        print('Serial', file=outfile)
    for fn in outlist:
        if not _args.normalize:
            fn = denormalize_id(fn)
        print(fn, file=outfile)
        nout += 1
    print(f'End dir2csv. {nout} row'
          f'{"" if nout == 1 else "s"}'
          f' written to {_args.csvfile}.')
