"""

"""
import argparse
import os.path
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.styles import numbers

from utl.normalize import sphinxify
from utl.readers import row_dict_reader, get_heading

NEWCOLS = ('Serial,Pages,Date,Person From,Person To,Org From,Org To,Type,'
           + 'Comment,Description')
NEWCOLS = NEWCOLS.split(',')
COLMAP = {'Multiple Images': 'Pages',
          'From': 'Person From',
          'To': 'Person To'}


def onefile(filename):
    workbook = Workbook()
    del workbook[workbook.sheetnames[0]]  # remove the default sheet
    ws = workbook.create_sheet('Sheet1')
    # infilename = os.path.join(_args.indir, filename)
    oldheading = get_heading(filename, _args.verbose, _args.skip_rows)

    # for row in row_dict_reader(infilename, _args.verbose,
    #                            _args.skip_rows):
    #     pass
    # workbook.save(os.path.join(_args.outdir, filename))
    return oldheading


def getparser():
    parser = argparse.ArgumentParser(description=sphinxify('''

                ''', calledfromsphinx))
    parser.add_argument('indir', help='''
        Input folder with CSV or XLSX files.
        ''')
    parser.add_argument('outdir', help='''
        Output folder to contain newly created files.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('--skip_rows', type=int, default=0, help='''
        Skip rows at the beginning of the CSV file.''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


calledfromsphinx = True


if __name__ == '__main__':
    calledfromsphinx = False
    assert sys.version_info >= (3, 9)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    heading = onefile(_args.indir)
    print(heading)
