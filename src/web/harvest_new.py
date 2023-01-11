"""
    For each file in a "candidate" folder, if that file is not in the "done"
    folder, copy it to a "staging" folder.
"""
import argparse
import csv
import os.path
import shutil
import sys

from utl.list_objects import list_objects
from utl.normalize import sphinxify
from utl.normalize import normalize_id, denormalize_id


def trace(level, template, *args):
    if verbose >= level:
        print(template.format(*args))


def getargs():
    parser = argparse.ArgumentParser(description='''
    For each file in a "candidate" folder, if that file is not in the "done"
    folder or any of its subfolders, copy it to a "staging" folder. Optionally
    check that the filename matches an object in the Modes database.
    
    Run list_needed.py before this script.
        ''')
    parser.add_argument('-c', '--candidate', required=True, help='''
        Directory containing new files that may need to be transferred''')
    parser.add_argument('-d', '--done', required=True, help='''
        Directory containing files already transferred,
        including sub-directories or a CSV file with the accession number
        in the first column''')
    parser.add_argument('-m', '--modes', required=False, help='''
        Modes XML database file. The accession numbers that are part of the
        candidate file names (like JB001.jpg) will be compared with the
        accession numbers in the XML file and only those that match will be
        harvested.''')
    # sdgroup = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('-s', '--staging', help='''
        Directory to contain files to be transferred. We copy files from the
        candidate directory to this directory.
        ''')
    parser.add_argument('--dryrun', action='store_true',
                        help=sphinxify('''
        Do not copy files. Just print info.''',
                                       calledfromsphinx))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


def getdonedir() -> dict[str]:
    donedir = _args.done
    done_files = {}
    # for donef in os.listdir(donedir):
    for dirpath, dirnames, filenames in os.walk(donedir):
        trace(2, f'{dirpath=}')
        for donef in filenames:
            donefile = donef.removeprefix('collection_').lower()
            if donefile.endswith('.jpg'):
                trace(3, f'   {donefile}')
                prefix, _ = os.path.splitext(donefile)
                try:
                    naccnum = normalize_id(prefix)
                except (ValueError, AssertionError) as e:
                    trace(1, '******** getdonedir: Bad format: {}, filename:{}, {}, {}',
                          prefix, donef, str(e), e.args)
                    continue
                done_files[naccnum] = os.path.join(dirpath, donef)
            elif not donefile.startswith('.'):  # ignore .DS_Store
                trace(2, f'----skipping {donef}')
    return done_files


def getdone() -> dict[str]:
    if os.path.isdir(_args.done):
        return getdonedir()
    # Not a directory, treat as CSV. The value in the dict will be just the
    # accession number as we don't have the path
    done_files = {}
    reader = csv.reader(_args.done)
    for row in reader:
        if row[0]:
            try:
                naccnum = normalize_id(row[0])
            except (ValueError, AssertionError) as e:
                trace(1, '******** Bad format in CSV, skipping row: {}, {}, {}',
                      row[0], str(e), e.args)
                continue
            done_files[naccnum] = row[0]
    return done_files


def harvest(candidatedir):
    global ncandidates, ncopied
    trace(1, 'Begin harvesting {}', candidatedir)
    for candidate in os.listdir(candidatedir):
        trace(3, 'In harvest(): candidate="{}"', candidate)
        candidatepath = os.path.join(candidatedir, candidate)
        if os.path.isdir(candidatepath):
            harvest(candidatepath)
            continue
        candidatex = candidate.removeprefix('collection_').lower()
        if candidate.startswith('.'):
            continue  # ignore .DS_Store
        ncandidates += 1
        prefix, _ = os.path.splitext(candidatex)
        try:
            naccnum = normalize_id(prefix)
        except (ValueError, AssertionError) as e:
            trace(1, '******** Bad format: candidate: "{}", prefix: "{}", '
                     'error: {}',
                  candidate, prefix,  str(e))
            continue
        if _args.modes:
            if naccnum not in objects:
                trace(1, f'******** Not in Modes: {prefix}')
                continue
        if naccnum in donefiles:
            trace(2, '******** Already done: {}', donefiles[naccnum])
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

    if not _args.dryrun and _args.staging and not os.path.isdir(_args.staging):
        print(_args.staging, 'is not a directory. Aborting.')
        sys.exit()
    verbose = _args.verbose
    ncandidates = ncopied = 0
    donefiles = getdone()
    objects = None
    if _args.modes:
        objectslist = list_objects(_args.modes)
        # Create a dict with the key of the normalized id and the value
        # being the original id.
        objects = {k: v for (k, v) in objectslist}
    harvest(_args.candidate)
    # print(donefiles)
    trace(1, '{} copied of {} candidates', ncopied, ncandidates)
