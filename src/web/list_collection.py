"""
"""
import argparse
import re
import sys

from utl.normalize import normalize_id, denormalize_id, DEFAULT_MDA_CODE


def getargs():
    parser = argparse.ArgumentParser(description='''
    Read the XML file downloaded from the website using the tools/export
    function, having selected "Media".

    Output is the list accession numbers of images in the collection.
        ''')
    parser.add_argument('infile', help='''
        The XML file downloaded from WordPress.''')
    parser.add_argument('outfile', help='''
        The output CSV file.''')
    parser.add_argument('-a', '--accession_number', action='store_true',
                        help='''
        If specified, the accession number is written. Otherwise the filename
        is written.
        ''')
    parser.add_argument('-m', '--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code, used in normalizing the accession number.
        The default is "{DEFAULT_MDA_CODE}".
        ''')
    parser.add_argument('-s', '--nosort', help='''
        By default the output is sorted by normalized accession number. this
        option inhibits the sort.
    ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    arguments = parser.parse_args()
    return arguments


def main1():
    accns = []
    for line in infile:
        if m := re.search(r'<wp:post_name><!\[CDATA\[(collection_.*)]]', line):
            if args.accession_number:
                accn = m.group(1).removeprefix('collection_')
                accn = accn.replace('-', '.')
                try:
                    naccn = normalize_id(accn)
                except ValueError:
                    # WordPress can add a numeric suffix to a name with
                    # JB1213.25 becoming JB1213.25.2 so strip off the trailing
                    # rubbish.
                    print(f'...retrying "{accn}"')
                    m = re.fullmatch(r'(.*\.\d+)\.\d+', accn)
                    if m:
                        naccn = normalize_id(m.group(1))
                    else:
                        print(f'cannot match {accn}')
                        continue
                accns.append(naccn)
            else:
                print(m.group(1), file=outfile)

    for naccn in sorted(accns):
        print(denormalize_id(naccn), file=outfile)


def main():
    accns = set()
    for line in infile:
        if m := re.search(r'<guid.*collection_(.*)\.jpg', line):
            naccn = normalize_id(m.group(1))
            if naccn in accns:
                print(f'Duplicate: {m.group(1)}')
            accns.add(naccn)
    for naccn in sorted(accns):
        print(denormalize_id(naccn), file=outfile)


if __name__ == '__main__':
    assert sys.version_info >= (3, 11)
    args = getargs()
    infile = open(args.infile)
    outfile = open(args.outfile, 'w')
    main()
