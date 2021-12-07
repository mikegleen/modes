"""
    For each serial number in a CSV file, move the corresponding file from
    the source directory to the destination directory or delete it.
"""
import argparse
import os.path
import re
import shutil
import sys


def trace(level, template, *args):
    if verbose >= level:
        print(template.format(*args))


def getargs():
    parser = argparse.ArgumentParser(description='''
    For each serial number in a CSV file, move the corresponding file from
    the source directory to the destination directory or just delete it.
        ''')
    parser.add_argument('source', help='''
        Source directory from which we will move or delete files.
        ''')
    parser.add_argument('-c', '--csvfile', required=True, help='''
        Contains accession numbers of files to be moved to another directory
        ''')
    parser.add_argument('-d', '--delete', help='''
        Delete the files; do not move them.''')
    parser.add_argument('-o', '--output', required=True, help='''
        Destination directory to contain files from the source directory
        ''')
    parser.add_argument('--dryrun', action='store_true', help='''
        Do not copy files. Just print info.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


def main():
    sourcedir = _args.source
    if not os.path.isdir(sourcedir):
        print(f'Not a directory: {sourcedir}')
        sys.exit()
    outputdir = _args.output
    if not os.path.isdir(outputdir):
        print(f'Not a directory: {outputdir}')
        sys.exit()
    dryrun = _args.dryrun
    sourcefiles = set(os.listdir(sourcedir))
    csvfile = open(_args.csvfile)
    nmoved = 0
    for objid in csvfile:
        objid = objid.strip()
        if not objid:
            continue
        found = False
        fn = objid + '.jpg'
        if fn in sourcefiles:
            found = True
        else:
            fn = 'collection_' + fn
            if fn in sourcefiles:
                found = True
        if found:
            sourcepath = os.path.join(sourcedir, fn)
            print(f'Moving {sourcepath}')
            nmoved += 1
            if not _args.dryrun:
                shutil.move(sourcepath, outputdir)
        else:
            print(f'Skipping {objid}')
    trace(1, '{} copied of {} candidates', nmoved, len(sourcefiles))


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    verbose = _args.verbose
    main()
