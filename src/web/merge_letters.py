"""
    From a root directory, examine each subdirectory. Process it if the format
    of the subdirectory name is:
        <accession #>  *or*
        <accession #>_<suffix>

    Each subdirectory contains scans of letters. The format of the filenames
    is documented in the file *Scanning Notes rev.4.docx* in the ../letters
    directory.

    For each letter, merge its JPEG images into a single PDF file.
"""
import argparse
import os
import sys
from collections import defaultdict
import re
from PyPDF2 import PdfFileMerger
from colorama import Style, Fore

from utl.normalize import normalize_id, sphinxify
from utl.readers import row_dict_reader


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def _onedir(ld, fd, subdirname: str, subdirpath: str):
    fnpat = r'(\w+)-(\d{3}).*\.pdf'
    for fn in os.listdir(subdirpath):
        trace(2, '    filename {}', fn)
        m = re.match(fnpat, fn)
        if m:
            an = m.group(1)  # accession #
            seq = m.group(2)
            if fn in ld[(an, seq)]:
                trace(1, 'Duplicate filename {}', fn,
                      color=Fore.RED)
            ld[(an, seq)].add(fn)
            fd[(an, seq)] = subdirpath
        # elif fn != '.DS_Store':
        else:
            trace(1, 'Ignored: {}/{}', subdirname, fn)


def get_letters_dict(indirname):
    """
    Called by main() below or callable from an external program.
    :param indirname: root folder containing subfolders
    :return: tuple containing:
                (1) dictionary mapping item number to its set of JPEG files
                    containing scans of the document's pages
                (2) dictionary mapping item number to its folder path. Needed
                    because not all images for an accession number are in the
                    same folder.
    """
    ld = defaultdict(set)
    fd = {}  # map accession number to its folder path
    for subdirname in os.listdir(indirname):
        trace(2, 'Subdirname: {}', subdirname)
        subdirpath = os.path.join(indirname, subdirname)
        if os.path.isdir(subdirpath):
            _onedir(ld, fd, subdirname, subdirpath)
        elif subdirname != '.DS_Store':
            trace(1, 'Ignored: {}', subdirname,
                  color=Fore.YELLOW)
    return ld, fd


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


def main():
    ld, fd = get_letters_dict(_args.indir)
    for anum_tuple, pages in sorted(ld.items()):
        trace(2, 'tuple = {}, pages = {}', anum_tuple, pages)
        anum = f'{anum_tuple[0]}.{int(anum_tuple[1])}'
        nanum = normalize_id(anum)
        if filterset and nanum not in filterset:
            continue
        pages = sorted(pages, key=skey)
        output = PdfFileMerger()
        subdirpath = fd[anum_tuple]
        for page in pages:
            output.append(os.path.join(subdirpath, page))
        outputpath = os.path.join(_args.outdir, anum + '.pdf')
        output.write(outputpath)


def get_filterset():
    """
    Read a CSV or XLSX file containing rows of objects, some of which are letters.
    The accession number is in column "Serial" and the type of object is in
    column "Type".

    :return: A set of normalized accession numbers of letters.
    """
    filterset = set()
    csvreader = row_dict_reader(_args.filter, _args.verbose, _args.skiprows)
    typefilter = _args.filter
    for row in csvreader:
        if row['Type'] == typefilter:
            filterset.add(normalize_id(row['Serial']))
    return filterset


def getparser():
    parser = argparse.ArgumentParser(description='''

    ''')
    parser.add_argument('indir', help='''
        Folder containing subfolders containing PDF files.''')
    parser.add_argument('outdir', help='''
        Output folder containing merged PDF files''')
    parser.add_argument('-f', '--filter', help='''
        spreadsheet containing Serial and Type columns. ''')
    parser.add_argument('--skiprows', type=int, default=0, help=sphinxify('''
        Skip rows at the beginning of the CSV file specified by --filter.
        ''', called_from_sphinx))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


called_from_sphinx = True


if __name__ == '__main__':
    called_from_sphinx = False
    assert sys.version_info >= (3, 11)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    if not os.path.isdir(_args.indir):
        raise ValueError(f'{_args.indir} is not a directory.')
    if _args.verbose < 2:
        sys.tracebacklimit = 0
    filterset = get_filterset() if _args.filter else None
    main()
