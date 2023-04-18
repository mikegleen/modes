"""
    For each serial number in a CSV file, move the corresponding file from
    the source directory to the destination directory or delete it.
"""
import argparse
import os.path
import re
import shutil
import subprocess
import sys

SIPSCMD = 'sips -s format jpeg "{}" -o "{}"'


def trace(level, template, *args):
    if verbose >= level:
        print(template.format(*args))


def sipscopy(sourcepath, outdir):
    sipscmd = SIPSCMD.format(sourcepath, outdir)
    trace(1, sipscmd)
    subprocess.check_call(sipscmd, shell=True)


def getargs():
    parser = argparse.ArgumentParser(description='''
    For each serial number in a CSV file, copy or move the corresponding file
    from the source directory to the destination directory or just delete it.
        ''')
    exgroup = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('source', help='''
        Source directory from which we will copy, move, or delete files.
        ''')
    exgroup.add_argument('--copy', action='store_true', help='''
        Copy the files.''')
    parser.add_argument('-c', '--csvfile', required=True, help='''
        Contains accession numbers of files to be moved to another directory
        ''')
    exgroup.add_argument('-d', '--delete', action='store_true', help='''
        Delete the files; do not move them.''')
    exgroup.add_argument('--move', action='store_true', help='''
        Move the files.''')
    parser.add_argument('-o', '--output', required=True, help='''
        Destination directory to contain files from the source directory
        ''')
    parser.add_argument('--dryrun', action='store_true', help='''
        Do not copy files. Just print info.''')
    parser.add_argument('-s', '--skiprows', type=int, default=0, help='''
        Number of lines to skip at the start of the CSV file''')
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

    sourcefiles = {}
    for fn in os.listdir(sourcedir):
        prefix, suffix = os.path.splitext(fn)
        sourcefiles[prefix] = fn, suffix
    csvfile = open(_args.csvfile)
    nmoved = 0
    for _ in range(_args.skiprows):
        print(f'Skipping {next(csvfile)}')
    for objid in csvfile:
        objid = objid.strip()
        if not objid:
            continue
        found = False
        fn = objid
        if fn in sourcefiles:
            found = True
        else:
            fn = 'collection_' + objid
            if fn in sourcefiles:
                found = True
        if found:
            suffix = sourcefiles[fn][1]
            sourcepath = os.path.join(sourcedir, sourcefiles[fn][0])
            action = ['Moving', 'Copying', 'Deleting'][int(_args.copy)
                                                       + int(_args.delete) * 2]
            print(f'{action} {sourcepath}')
            nmoved += 1
            if _args.dryrun:
                continue
            if _args.copy:
                if suffix.lower() == 'jpg':
                    shutil.copy(sourcepath, outputdir)
                else:
                    sipscopy(sourcepath, outputdir)
            elif _args.move:
                shutil.move(sourcepath, outputdir)
            else:
                os.remove(sourcepath)
        else:
            print(f'Skipping {objid}')
    trace(1, '{} copied of {} candidates', nmoved, len(sourcefiles))


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    verbose = _args.verbose
    main()
