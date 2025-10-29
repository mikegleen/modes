"""
    Update the <Production/Place> element. Remove the children <County> and <Country>.
"""

import argparse
import codecs
import csv
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.readers import object_reader


def opencsvwriter(filename):
    # csvfile = open(filename, 'w', newline='')
    csvfile = codecs. open(filename, 'w', 'utf-8-sig')
    outcsv = csv.writer(csvfile)
    # outcsv.writerow(HEADING)
    return outcsv


def oneobj(idnum, obj):
    parent = obj.find('./' + _args.tag)  # will barf if doesn't exist
    if parent is None:  # delete the elementtype=placeholder objects
        # print(f'No find {_args.tag}, {idnum=}')
        return
    row = [idnum]
    for child in parent:
        row.append(child.tag)
    csvwriter.writerow(row)

def main():
    for idnum, obj in object_reader(_args.inxmlfile):
        oneobj(idnum, obj)


def getparser() -> argparse.ArgumentParser:
    """
    Called either by getargs() in this file or by Sphinx.
    :return: an argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser(description='''
        Write a CSV file with the tag names of the children of the --tag element
    ''')
    parser.add_argument('-i', '--inxmlfile')
    parser.add_argument('-o', '--outcsvfile', help='''
        The output CSV file.''')
    parser.add_argument('-t', '--tag', required=True, help='''The element whose children are to be listed''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary
        information.''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    #
    # commented out because I can't remember why I wrote it.
    # if args.addendum:
    #     args.addendum = args.addendum.lower()

    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 13)
    _args = getargs(sys.argv)
    csvwriter = opencsvwriter(_args.outcsvfile)
    main()

