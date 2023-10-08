"""
    From a root directory, examine each subdirectory. Process it if the format
    of the subdirectory name is:
        <accession #>  *or*
        <accession #>_<suffix>

    Each subdirectory contains scans of letters. The format of the filenames
    is documented in the file *Scanning Notes rev.4.docx* in the ../letters
    directory.

"""
import argparse
import codecs
import csv
import os
import sys
from collections import defaultdict
import re

from colorama import Style, Fore


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def _onedir(ld, subdirname: str):
    fnpat = r'(\w+)-(\d{3}).*\.(jpg|jpeg)'
    for fn in os.listdir(os.path.join(_args.indir, subdirname)):
        m = re.match(fnpat, fn)
        if m:
            an = m.group(1)  # accession #
            seq = m.group(2)
            ld[(an, seq)].append(fn)
        elif fn != '.DS_Store':
            trace(1, 'Ignored: {}/{}', subdirname, fn)


def get_letters_dict(indirname):
    """
    Called by main() below or callable from an external program.
    :param indirname: root folder containing subfolders
    :return: dictionary mapping item number to its list of jpg files containing
             scans of the document's pages
    """
    ld = defaultdict(list)
    for subdirname in os.listdir(indirname):
        subdirpath = os.path.join(indirname, subdirname)
        if os.path.isdir(subdirpath):
            _onedir(ld, subdirname)
        elif subdirname != '.DS_Store':
            trace(1, 'Ignored: {}', subdirname,
                  color=Fore.YELLOW)
    return ld


def skey(s):
    prefix, suffix = os.path.splitext(s)
    parts = prefix.split('-')
    len_parts = len(parts)
    if len_parts not in (2, 3):
        raise ValueError(f'{s} parse error in skey')
    if len_parts == 2:
        return s
    part3 = parts[2]
    try:
        p3i = f'{int(part3):03}'
    except ValueError:
        # Assume trailing A or B
        p3i = f'{int(part3[:-1]):03}{part3[-1]}'
    return f'{parts[0]}-{parts[1]}-{p3i}{suffix}'


def validpages(pages):
    """
    Verify that a document doesn't contain both two part filenames
    like "JB1000-001.jpg" and three part filenams like "JB1000-001-1.jpg

    :param pages: list of strings containing names of JPEG files
    :return: None. Prints error messages.
    """
    nparts = defaultdict(bool)
    for page in pages:
        prefix, suffix = os.path.splitext(page)
        parts = prefix.split('-')
        len_parts = len(parts)
        nparts[len_parts] = True
        # print(parts)
        # print(nparts)
    if nparts[2] and nparts[3]:
        print(f'Bad parse: {sorted(pages, key=skey)}')


def main():
    ld = get_letters_dict(_args.indir)
    encoding = 'utf-8-sig'
    csvfile = codecs.open(_args.outfile, 'w', encoding)
    outcsv = csv.writer(csvfile)
    for anum_tuple, pages in sorted(ld.items()):
        anum = f'{anum_tuple[0]}.{int(anum_tuple[1])}'
        row = [anum] + sorted(pages, key=skey)
        outcsv.writerow(row)
        validpages(pages)


def getparser():
    parser = argparse.ArgumentParser(description='''

    ''')
    parser.add_argument('indir', help='''
        Folder containing subfolders containing images.''')
    parser.add_argument('outfile', help='''
        Output filename for the CSV file. This file contains the accession
        number with the document number appended in column A and filenames of
        scans of the document's pages in subsequent columns. ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 11)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    if not os.path.isdir(_args.indir):
        raise ValueError(f'{_args.indir} is not a directory.')
    if _args.verbose < 2:
        sys.tracebacklimit = 0

    main()
