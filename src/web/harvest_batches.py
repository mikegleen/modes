"""
    For each file in a "website" folder's child folders that starts with "collection_",
    copy that file to a "staging" folder, stripping off the "collection_" preamble.
"""
import argparse
import os.path
import shutil
import sys

from utl.normalize import sphinxify

PREFIX = 'collection_'

def trace(level, template, *args):
    if verbose >= level:
        print(template.format(*args))


def getparser():
    parser = argparse.ArgumentParser(description='''
    For each file in a directory and subdirectories, copy it to an output directory.
    Remove the "collection_" prefix.
        ''')
    parser.add_argument('-i', '--indir', required=True, help='''
        Directory containing new files to be transferred''')
    parser.add_argument('-o', '--outdir', required=True, help=sphinxify('''
        We copy files from the
        input directory and its child directories to this directory.
        ''', calledfromsphinx))
    parser.add_argument('--dryrun', action='store_true',
                        help=sphinxify('''
        Do not copy files. Just print info. --verbose is set to 2 unless it is already
        set other than 1.''', calledfromsphinx))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs():
    parser = getparser()
    args = parser.parse_args()
    if args.dryrun and args.verbose == 1:
        args.verbose = 2
    return args


def harvest(batchdir):
    global ncandidates, ncopied
    trace(1, 'Begin harvesting {}', batchdir)
    for candidate in os.listdir(batchdir):
        frompath = os.path.join(batchdir, candidate)
        if os.path.isdir(frompath):
            harvest(frompath)
            continue
        ncandidates += 1
        if not candidate.startswith(PREFIX):
            trace(2, 'Skipping (no prefix) {}', frompath)
            continue
        if '-' in candidate:
            trace(2, 'Skipping (item number) {}', frompath)
            continue
        trace(3, 'In harvest(): candidate="{}"', candidate)
        candidatex = candidate.removeprefix(PREFIX)
        prefix, suffix = os.path.splitext(candidatex)
        candidatex = prefix.upper() + suffix.lower()
        targetpath = os.path.join(_args.outdir, candidatex)
        ncopied += 1
        trace(2, 'harvesting: from {}, to directory {}', frompath, targetpath)
        if not _args.dryrun:
            shutil.copy(frompath, targetpath)


def main(webdir):
    for folder in os.listdir(webdir):
        folderpath = os.path.join(webdir, folder)
        if os.path.isdir(folderpath):
            harvest(folderpath)

calledfromsphinx = True
if __name__ == '__main__':
    calledfromsphinx = False
    assert sys.version_info >= (3, 13)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs()

    if not os.path.isdir(_args.outdir):
        print(_args.outdir, 'is not a directory. Aborting.')
        sys.exit(1)
    verbose = _args.verbose
    ncandidates = ncopied = 0
    harvest(_args.indir)
    # print(donefiles)
    trace(1, '{} copied of {} candidates', ncopied, ncandidates)
