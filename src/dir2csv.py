"""
    Read a directory of JPEG files and create a CSV file with one column
    containing the filename minus the trailing .jpg
    A heading row of 'Serial' precedes the data.
"""
import os.path
import re
import sys


def dir2csv(jpegdir):
    jpglist = list()
    jpgfiles = os.listdir(jpegdir)
    for jpgfile in jpgfiles:
        m = re.match(r'(collection_)?(.+)\.jpg', jpgfile)
        if not m:
            print(f'dir2csv skipping: {jpgfile}')
            continue
        jpglist.append(m.group(2))
    return jpglist


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    if len(sys.argv) != 3:
        print('Parameters: input folder, output csv')
        sys.exit()
    indir = sys.argv[1]
    outfile = open(sys.argv[2], 'w')

    files = os.listdir(indir)
    outlist = dir2csv(indir)
    nout = 0
    print('Serial', file=outfile)
    for fn in outlist:
        print(fn, file=outfile)
        nout += 1
    print(f'End dir2csv. {nout} rows written.')
