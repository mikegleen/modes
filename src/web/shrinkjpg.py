"""
    Iterate over jpg files in a directory. If the maximum dimension (height or
    width) is greater than 1000 pixels, shrink the file.
"""
import argparse
import os
from PIL import Image
from shutil import copy2
import subprocess
import sys

from utl.normalize import if_not_sphinx, sphinxify

DEFAULT_MAXPIXELS = 1000
SIPSCMD = 'sips -s format jpeg -Z {} "{}" -o "{}"'


def trace(level, template, *args):
    if VERBOSE >= level:
        print(template.format(*args))


def getargs():
    parser = argparse.ArgumentParser(description='''
        For every JPG file in a directory, copy it to the output directory or, if
        it is large, copy a shrunken version of it.''')
    parser.add_argument('indir', help='''
        Input directory''')
    parser.add_argument('outdir', help='''
        Output directory''')
    parser.add_argument('--dryrun', action='store_true', help=sphinxify('''
        Print messages but don't do processing. Implies  --verbose=2''',
                        calledfromsphinx))
    parser.add_argument('-m', '--maxpixels', type=int,
                        default=DEFAULT_MAXPIXELS, help=
                        '''
        Maximum number of pixels in either dimension.'''
                        + if_not_sphinx(f''' The
                         default is {DEFAULT_MAXPIXELS} pixels.''',
                                        calledfromsphinx
                                        ))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    if args.dryrun:
        args.verbose = 2
    return args


def main():
    indir = _args.indir
    outdir = _args.outdir
    maxpixels = _args.maxpixels
    dryrun = _args.dryrun
    files = os.listdir(indir)
    ncopied = 0
    nshrunk = 0
    for filename in files:
        prefix, suffix = os.path.splitext(filename)
        filepath = os.path.join(indir, filename)
        if suffix.lower() not in ('.jpg', '.png'):
            trace(1, 'skipping {}', filename)
            continue
        with Image.open(filepath) as im:
            width, height = im.size
        if max(width, height) > maxpixels:
            sipscmd = SIPSCMD.format(maxpixels, filepath, outdir)
            trace(2, 'width = {}, height = {}, command = {}', width, height,
                  sipscmd)
            nshrunk += 1
            if dryrun:
                continue
            subprocess.check_call(sipscmd, shell=True)
        else:
            trace(2, 'copying {} --> {}', filepath, outdir)
            ncopied += 1
            if dryrun:
                continue
            copy2(filepath, outdir)
    trace(1, '{} copied\n{} shrunk', ncopied, nshrunk)


calledfromsphinx = True
if __name__ == '__main__':
    calledfromsphinx = False
    assert sys.version_info >= (3, 9)
    _args = getargs()
    if not os.path.isdir(_args.indir):
        raise ValueError('Input must be a directory.')
    if not os.path.isdir(_args.outdir):
        os.mkdir(_args.outdir)
    VERBOSE = _args.verbose
    main()
