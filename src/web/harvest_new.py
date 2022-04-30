"""
    For each file in a "candidate" folder, if that file is not in the "done"
    folder, copy it to a "staging" folder.
"""
import argparse
import os.path
import shutil
import sys

from utl.normalize import sphinxify


def trace(level, template, *args):
    if verbose >= level:
        print(template.format(*args))


def getargs():
    parser = argparse.ArgumentParser(description='''
    For each file in a "candidate" folder, if that file is not in the "done"
    folder or any of its subfolders, copy it to a "staging" folder. Run
    list_needed.py before this script.
        ''')
    parser.add_argument('-c', '--candidate', required=True, help='''
        Directory containing new files that may need to be transferred''')
    parser.add_argument('-d', '--done', required=True, help='''
        Directory containing files already transferred,
        including sub-directories''')
    parser.add_argument('-s', '--staging', required=True, help='''
        Directory to contain files to be transferred. We copy files from the
        candidate directory to this directory.
        ''')
    parser.add_argument('--dryrun', action='store_true', help=sphinxify('''
        Do not copy files. Just print info. Implies --verbose 2.''',
                        calledfromsphinx))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    if args.dryrun:
        args.verbose = max(2, args.verbose)
    return args


def getdone() -> dict[str]:
    donedir = _args.done
    done_files = {}
    # for donef in os.listdir(donedir):
    for dirpath, dirnames, filenames in os.walk(donedir):
        trace(2, f'{dirpath=}')
        for donef in filenames:
            donefile = donef.removeprefix('collection_').lower()
            if donefile.endswith('jpg'):
                trace(3, f'   {donefile}')
                # done_files.add(donefile)
                done_files[donefile] = os.path.join(dirpath, donef)
            elif not donefile.startswith('.'):  # ignore .DS_Store
                trace(2, f'----skipping {donef}')
    return done_files


def harvest(done_files: dict[str]):
    global ncandidates, ncopied
    candidatedir = _args.candidate
    trace(1, 'Begin harvesting {}', candidatedir)
    for candidate in os.listdir(candidatedir):
        candidatex = candidate.removeprefix('collection_').lower()
        ncandidates += 1
        if candidatex in done_files or candidate.startswith('.'):
            if candidate.startswith('.'):
                ncandidates -= 1  # don't count .DS_Store
            else:
                trace(1, 'already done: {}', done_files[candidatex])
        else:
            ncopied += 1
            frompath = os.path.join(candidatedir, candidate)
            trace(1, 'harvesting: {}', candidate)
            trace(2, '    from {}, to directory {}', frompath, _args.staging)
            if not _args.dryrun:
                shutil.copy(frompath, _args.staging)


calledfromsphinx = True
if __name__ == '__main__':
    calledfromsphinx = False
    assert sys.version_info >= (3, 9)
    _args = getargs()
    verbose = _args.verbose
    ncandidates = ncopied = 0
    donefiles = getdone()
    harvest(donefiles)
    # print(donefiles)
    trace(1, '{} copied of {} candidates', ncopied, ncandidates)
