"""
    For each file in a "candidate" folder, if that file is not in the "done"
    folder, copy it to a "harvested" folder.
"""
import argparse
import os.path
import re
import shutil
import sys


def trace(level, template, *args):
    if VERBOSE >= level:
        print(template.format(*args))


def getargs():
    parser = argparse.ArgumentParser(description='''
    For each file in a "candidate" folder, if that file is not in the "done"
    folder, copy it to a "harvested" folder.
        ''')
    parser.add_argument('-c', '--candidate', required=True, help='''
        Directory containing new files that may need to be transferred''')
    parser.add_argument('-d', '--done', required=True, help='''
        Directory containing files already transferred''')
    parser.add_argument('-s', '--staging', required=True, help='''
        Directory to contain files to be transferred
        ''')
    parser.add_argument('--dryrun', action='store_true', help='''
        Do not copy files. Just print info.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    VERBOSE = _args.verbose
    donedir = _args.done
    candidatedir = _args.candidate
    stagingdir = _args.staging
    donefiles = set()
    for donef in os.listdir(donedir):
        donefile = donef.removeprefix('collection_')
        donefiles.add(donefile)
    ncandidates = ncopied = 0
    for candidate in os.listdir(candidatedir):
        ncandidates += 1
        if candidate in donefiles:
            trace(1, 'skipping: {}', candidate)
        else:
            ncopied += 1
            frompath = os.path.join(candidatedir, candidate)
            topath = os.path.join(stagingdir, candidate)
            trace(1, 'harvesting: {}', candidate)
            trace(2, 'from {}, to {}', frompath, topath)
            if not _args.dryrun:
                shutil.copy(frompath, topath)
    trace(1, '{} copied of {} candidates', ncopied, ncandidates)