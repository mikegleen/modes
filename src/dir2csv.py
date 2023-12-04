"""
    Read a directory of JPEG files and create a CSV file with columns
    containing the accession number and location.

    The location is extracted from the part of the filename between '``--``' and
    the trailing '.jpg', such as ``JB1224.002--G18``.

    Handle formats like::

     JB1223.jpg
     JB1223-001.jpg
     JB1234-001B.jpg    includes verso
     JB1234-001-1.jpg   includes page # if more than 1 page
     JB1234-001-1A.jpg  <accn #>-<sub #>-<page #><recto>
     JB1234-1.jpg       <accn #>-<page #>
     JB1234-A.jpg       <accn #>-<recto>

"""
import argparse
import os.path
import re
import sys
from utl.normalize import normalize_id, denormalize_id


def dir2listsub(jpegdir):
    """

    :param jpegdir:
    :return: dict of accn# -> 'serial,location'
    """
    # Use a dict because we can have multiple pages for each accn.
    jpgdict = dict()
    jpgfiles = os.listdir(jpegdir)
    print_normalized = _args.normalize
    for jpgfile in jpgfiles:
        jpgfile = jpgfile.removeprefix('collection_')
        m = re.fullmatch(r'(.*)\.(jpg|jpeg)', jpgfile)
        if not m:
            if jpgfile != '.DS_Store':
                print(f'dir2listsub skipping, cannot find jpg|jpeg {jpgfile}')
            continue
        prefix = m[1]  # remove trailing .jpg
        parts = prefix.split('--')
        location = parts[1] if len(parts) > 1 else _args.location
        m = re.match(r'(\w+)-(\d{3})', prefix)
        if m:
            accn = f'{m[1]}.{int(m[2])}'
        else:
            # could be just the accession # without the subnumber
            m = re.match(r'(.*?)(-.*)?$', prefix)
            if not m:
                print(f'dir2listsub skipping: {jpgfile}')
                continue
            accn = m[1]
        try:
            # print(f'{accn=}')
            naccn = normalize_id(accn, verbose=2)
        except ValueError:
            if _args.nostrict:
                print(f'Cannot normalize {accn}, ignored.')
                continue
            else:
                print(f'Cannot normalize {accn}, aborting.  Specify --nostrict'
                      f' to allow (and ignore) these files.')
                sys.exit(1)
        if print_normalized:
            accn = naccn
        else:
            # Make sure the accession number is in canonical form.
            accn = denormalize_id(naccn)
        jpgdict[naccn] = (accn, location)
    return [x[1] for x in sorted(jpgdict.items())]  # discard keys


def getparser():
    parser = argparse.ArgumentParser(description='''
        For every JPG file in a directory write the name minus the trailing
        ".jpg" to a CSV file.

        The filenames include a 3-digit sub-number following a '-', possibly
        followed by another '-' and a page number. The subnumber has leading
        zeros removed and appended to the accession number following a full stop.
        Trailing page numbers are discarded. If multiple pages are found for a
        single object, only one row is written to the CSV file.
        ''')
    parser.add_argument('indir', help='''
        Folder containing images to list''')
    parser.add_argument('csvfile', help='''
        Output CSV file containing the accession numbers extracted from the filenames
        in indir''')
    parser.add_argument('--heading', action='store_true', help='''
        Write a row at the front of the CSV file containing ``Serial,Location``.
        ''')
    parser.add_argument('-l', '--location', default="", help='''
        The location to use if the ``--loc`` field doesn't exist in the filename.
        ''')
    parser.add_argument('-n', '--normalize', action='store_true', help='''
        Normalize the accession number written to the CSV file.
        ''')
    parser.add_argument('-t', '--nostrict', action='store_true', help='''
        Ignore a row containing an accession number that cannot be normalized. Otherwise abort.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


def main():
    outlist = dir2listsub(indir)
    nout = 0
    if _args.heading:
        print('Serial,Location', file=outfile)
    for row in outlist:
        # print(f'{row=}')
        print(','.join(row), file=outfile)
        nout += 1
    return nout


if __name__ == '__main__':
    assert sys.version_info >= (3, 11)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    print('Begin dir2csv.')
    indir = _args.indir
    outfile = open(_args.csvfile, 'w')
    nwritten = main()
    print(f'End dir2csv. {nwritten} row'
          f'{"" if nwritten == 1 else "s"}'
          f' written to {_args.csvfile}.')
