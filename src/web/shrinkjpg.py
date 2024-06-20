"""
    Iterate over jpg files in a directory. If the maximum dimension (height or
    width) is greater than 1000 pixels, shrink the file.

    If option -i is given:
        Shrink the images so that it is 72 pixels per inch.
"""
import argparse
import re
from collections import namedtuple
import os
from PIL import Image
from shutil import copy2
import subprocess
import sys

from colorama import Fore, Style

from utl.normalize import if_not_sphinx, sphinxify, normalize_id
from utl.readers import object_reader

DEFAULT_MAXPIXELS = 1000
DEFAULT_PPI = 72  # Pixels per inch
SIPSCMD = 'sips -s format jpeg -Z {} "{}" -o "{}"'
Reading = namedtuple('Reading', 'height width')


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def getparser():
    parser = argparse.ArgumentParser(description='''
        For every JPG file in a directory, copy it to the output directory or, if
        it is large, copy a shrunken version of it.''')
    parser.add_argument('indir', help='''
        Input directory''')
    parser.add_argument('outdir', help='''
        Output directory''')
    parser.add_argument('--dryrun', action='store_true', help=sphinxify('''
        Print messages but don't do processing. Implies  --verbose = 2''',
                        calledfromsphinx))
    parser.add_argument('-m', '--maxpixels', type=int,
                        default=DEFAULT_MAXPIXELS, help='''
        Maximum number of pixels in either dimension.'''
                        + if_not_sphinx(f''' The
                         default is {DEFAULT_MAXPIXELS} pixels.''',
                                        calledfromsphinx
                                        ))
    parser.add_argument('-i', '--inxml',
                        help=sphinxify('''If specified, reduce the size
                  of the image so that it is 72 pixels per inch.
                  This parameter names the Modes XML file from which to extract
                  the height and width of images. The target pixels per inch
                  can be varied using the --ppi parameter. Note that
                  the measurements in the XML file are approximate and may not
                  exactly match the image size.''', calledfromsphinx))
    parser.add_argument('--ppi', type=int, default=DEFAULT_PPI, help='''
        Set the number of pixels per inch in the output image.'''
                        + if_not_sphinx(f''' The default is {DEFAULT_PPI}.''', calledfromsphinx))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs():
    parser = getparser()
    args = parser.parse_args()
    if args.dryrun:
        args.verbose = 2
    return args


def normalize_prefix(prefix: str):
    prefix = prefix.removeprefix('collection_')
    try:
        nidnum = normalize_id(prefix)
    except ValueError:
        nidnum = None
    return nidnum


def new_hxw(xh, xw, ih, iw) -> (int, int):
    """

    :param xh: XML height in mm
    :param xw: XML width in mm
    :param ih: image height in pixels
    :param iw: image width in pixels
    :return: new image (height, width) in pixels
    """
    pixels_per_mm = _args.ppi / 25.4
    newh = min(xh * pixels_per_mm, float(ih))
    neww = min(xw * pixels_per_mm, float(iw))
    newh = int(round(newh))
    neww = int(round(neww))
    return newh, neww


def call_sips(img_height, img_width, filepath, outdir):
    maxpixels = max(img_height, img_width)
    sipscmd = SIPSCMD.format(maxpixels, filepath, outdir)
    trace(2, 'height = {}, width = {}, command = {}', img_height, img_width,
          sipscmd)
    if _args.dryrun:
        return
    subprocess.check_call(sipscmd, shell=True)


def main():
    indir = _args.indir
    outdir = _args.outdir
    maxpixels = _args.maxpixels
    dryrun = _args.dryrun
    files = os.listdir(indir)
    ncopied = 0
    nshrunk = 0
    for filename in files:
        trace(2, 'Filename: {}', filename)
        prefix, suffix = os.path.splitext(filename)
        filepath = os.path.join(indir, filename)
        if suffix.lower() not in ('.jpg', '.png'):
            trace(1, 'skipping {}', filename)
            continue
        with Image.open(filepath) as im:
            img_width, img_height = im.size
        if _args.inxml:
            nidnum = normalize_prefix(prefix)
            trace(3, 'Normalized id: {}', nidnum)
            try:
                xh, xw = readings[nidnum]
            except KeyError:
                trace(1, "No find filename {}, nidnum: {}", filename, nidnum, color=Fore.RED)
                continue
            newh, neww = new_hxw(xh, xw, img_height, img_width)
            trace(3, 'XML H,W: {}mm,{}mm Orig img H,W: {}px,{}px', xh, xw, img_height, img_width)
            call_sips(newh, neww, filepath, outdir)
            nshrunk += 1
            continue
        if max(img_width, img_height) > maxpixels:
            sipscmd = SIPSCMD.format(maxpixels, filepath, outdir)
            trace(2, 'width = {}, height = {}, command = {}', img_width, img_height,
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


def get_readings():
    for idnum, elem in object_reader(_args.inxml):
        # print('nxt', idnum)
        reading = elem.find('./Description/Measurement[Part="Image"]/Reading')
        if reading is not None:
            nidnum = normalize_id(idnum)
            rtext = reading.text.replace(' ', '') if reading.text else ''
            m = re.match(r'(\d+)[Xx](\d+)', rtext)
            if m:
                readings[nidnum] = Reading(int(m[1]), int(m[2]))
                # print(idnum, readings[nidnum])


calledfromsphinx = True
if __name__ == '__main__':
    readings = dict()
    calledfromsphinx = False
    assert sys.version_info >= (3, 9)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs()
    if not os.path.isdir(_args.indir):
        raise ValueError('Input must be a directory.')
    if not os.path.isdir(_args.outdir):
        os.mkdir(_args.outdir)
    VERBOSE = _args.verbose
    if _args.inxml:
        get_readings()
    main()
