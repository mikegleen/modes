"""
    Search the named folders and return the path to the most recent file based on the
    ISO-formatted front part of the filename and an optional suffix.

    Files are of the format yyyy-mm-dd[a]_some_other_text.xml

    [a] is an optional suffix in the case where there are more files created in one day.
    It can be any single case-insensitve alphabetic character.

    Folder names beginning with '#' are ignored.

    An example runstream using x066_latest.py is::

        #!/bin/zsh
        set -e
        INXML=`python src/utl/x066_latest.py -i prod_update/normal`
        echo INXML= $INXML
        python src/exhibition.py $INXML --verify

"""

import argparse
from datetime import datetime, timedelta
import os.path
import re
import sys

from utl.normalize import sphinxify, if_not_sphinx


def getparser():
    parser = argparse.ArgumentParser(description=__doc__)
    megroup = parser.add_mutually_exclusive_group(required=True)
    megroup.add_argument('-i', '--indir', help='''
        Folder to search.''')
    megroup.add_argument('-f', '--listfile', help='''
        File containing multiple folders to search, one per line.''')
    parser.add_argument('-n', '--newxml', help='''
        Name of file to compare against the tentative newest in the named folder(s).
        Skip this file since it is the name of the file we are creating. This is not
        the first run of this script.''')
    parser.add_argument('-m', '--modify', action='store_true', help=sphinxify('''
        If specified, append the value of --modify_text to the date portion of the filename.
        2026-03-15_prod_save becomes 2026-03-15s_prod_save. Used by script
        sort_prod_save.sh so that x066_latest.py will select the sorted file
        to use as input.''', calledfromsphinx))
    parser.add_argument('--modify_text', default='s', help='''
        The optional text to append to the date part of the filename.''' +
        if_not_sphinx(''' Default = 's'. ''', calledfromsphinx))
    parser.add_argument('--re', help='''
        If specified, files must match this regular expression to be considered.''')
    parser.add_argument('-s', '--strict', action='store_true', help='''
    If set, abort if we are using the output file as input. This would happen
    if we re-run a script without previously deleting the output file. If not set,
    check for the output file and skip it, issuing a warning.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


def onedir(dirname):
    onedir_datetime = datetime(1970, 1, 1)
    onedir_path = None
    for filename in os.listdir(dirname):
        if _args.newxml and _args.newxml == filename:
            if _args.strict:
                raise ValueError('Cannot use output file for input.')
            print(f'Skipping {filename}', file=sys.stderr)
            continue
        path = os.path.join(dirname, filename)
        if not (os.path.isfile(path) and filename.lower().endswith('.xml')):
            continue
        if len(filename) < 15:
            print(f'Short filename, ignored: {filename}')
            raise ValueError(f'Badly formed filename: {path}. Short filename: \'{filename}\'')
        try:
            isodate = datetime.fromisoformat(filename[:10])
        except ValueError as err:
            raise ValueError(f'Badly formed filename: {path}. {err}')
        if _args.re:
            m = re.match(_args.re, filename)
            if not m:
                continue
        suffix = filename[10].lower()
        minutes = timedelta()
        if suffix.isalpha():
            minutes = timedelta(minutes=ord(suffix) - ord('a') + 1)
        isodate += minutes
        if isodate > onedir_datetime:
            onedir_datetime = isodate
            onedir_path = path
    return onedir_datetime, onedir_path


def main(args):
    latest_datetime = datetime(1970, 1, 1)
    latest_path = None
    if args.indir:
        latest_datetime, latest_path = onedir(args.indir)
    elif args.listfile:
        for row in open(args.listfile):
            if row.startswith('#'):
                continue
            onedir_datetime, onedir_path = onedir(row.strip())
            # print("xxx", row.strip(), onedir_datetime, onedir_path, file=sys.stderr)
            if onedir_datetime > latest_datetime:
                latest_path = onedir_path
                latest_datetime = onedir_datetime
                # print(f'{latest_path=}', file=sys.stderr)
    if latest_path:
        if _args.modify:
            m = re.match(r'(.*\d{4}-\d\d-\d\d)(.*)', latest_path)
            if not m:
                raise ValueError(f'path found: ({latest_path}) failed match.')
            latest_path = m[1] + args.modify_text + m[2]
        print(latest_path, end='')
    else:
        raise ValueError('Cannot find path.')


calledfromsphinx = True
if __name__ == '__main__':
    assert sys.version_info >= (3, 13)
    sys.tracebacklimit = 0
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    calledfromsphinx = False
    _args = getargs(sys.argv)
    main(_args)
