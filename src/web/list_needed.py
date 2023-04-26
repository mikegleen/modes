"""
For every ID in a CSV file or every filename in a folder, report if the
corresponding image is not in a folder.

"""
import argparse
import csv
import os.path
import sys
from utl.excel_cols import col2num
from utl.list_objects import list_objects
from utl.normalize import normalize_id, denormalize_id


def trace(level, template, *args):
    if VERBOSE >= level:
        print(template.format(*args))


def getparser():
    parser = argparse.ArgumentParser(description='''
    For every ID in a CSV file, report if the corresponding image is not in a
    folder. This should be run before harvest_new.py.''')
    parser.add_argument('imgdir', help='''
        Folder containing images or subfolders containing images we already
        have. Only one level of subfolder is examined.''')
    parser.add_argument('-c', '--candidatefile',  help='''
        CSV file containing the list of new objects or a directory containing
        jpg files with names consisting of the accession numbers. If omitted
        then the objects in the Modes file will be the candidates, showing
        all of the objects in Modes for which we don't have images.''')
    parser.add_argument('--col_acc', type=str, default='0', help='''
        The zero-based column containing the accession number (ID) of the
        object we are searching for. The default is column zero.  The column
        can be a number or a spreadsheet-style letter.''')
    parser.add_argument('-i', '--invert', action='store_true', help='''
        Report if the image **IS** in the folder.''')
    parser.add_argument('-m', '--modesfile', required=True, help='''
        File to search for valid accession numbers.''')
    parser.add_argument('-r', '--reportfile', help='''
        File to contain a list of the images that we have.''')
    parser.add_argument('-o', '--outfile', help='''
        Output file. Default is sys.stdout''')
    parser.add_argument('-s', '--skip_rows', type=int, default=0, help='''
        Skip rows at the beginning of the CSV file.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs():
    parser = getparser()
    args = parser.parse_args()
    args.col_acc = col2num(args.col_acc)
    # print(f'{args.col_acc=}')
    return args


def build_img_dict(img_ids: dict, imgdir: str):
    """
    Build a set of normalized accession numbers from the folders containing
    images.
    :return: A dict with key of the normalized id and value a tuple of the file
             name without possible leading "collection_" and the path.
    """
    def onefile(imgf: str):
        imgf2 = imgf.removeprefix('collection_')
        prefix, suffix = os.path.splitext(imgf2)
        if suffix.lower() not in ('.jpg', '.png'):
            if _args.verbose > 1 and not imgf.startswith('.'):  # ignore .DS_Store
                trace(1, 'not image: {}', imgf)
            return
        try:
            nid = normalize_id(prefix)
        except ValueError as ve:
            print(f'Skipping {imgf}: {ve}')
            return
        if nid in img_ids:
            trace(2, f'Duplicate: {prefix} in {dirpath.removeprefix(_args.imgdir)},'
                  f' original in {img_ids[nid][1].removeprefix(_args.imgdir)}')
        else:
            img_ids[nid] = (imgf2, dirpath)

    for subfile in sorted(os.listdir(imgdir)):
        dirpath = os.path.join(imgdir, subfile)
        if os.path.isdir(dirpath):
            trace(2, 'Folder {}', dirpath)
            build_img_dict(img_ids, dirpath)
        else:
            onefile(subfile)
            continue
    return


def build_candidate_set(valid_idnums):
    """
    From a CSV file or a folder of JPG files, extract a set of accession
    numbers that we want.
    :param valid_idnums: The set of normalized accession numbers extracted
           from a Modes XML file
    :return:
    """

    def add_one_id(candidate):
        """
        :param candidate: filename with trailing .csv removed
        :return: None. The nonlocal candidate_set is updated if the name
                 was valid.
        """
        nonlocal notinmodes
        candidate2 = candidate.removeprefix('collection_')
        try:
            normid = normalize_id(candidate2)
        except ValueError as ve:
            if not candidate2.startswith('.'):
                trace(1, '{}', ve)
            return
        if normid in valid_idnums:
            candidate_set.add(normid)
        else:
            trace(2, 'Skipping {}, not in Modes.', candidate2)
            notinmodes += 1

    notinmodes = 0
    candidate_set = set()
    trace(2, "Building candidate set.")
    if os.path.isdir(_args.candidatefile):
        candidates = [os.path.splitext(f)[0]
                      for f in os.listdir(_args.candidatefile)]
        for c in candidates:
            add_one_id(c)
    else:
        reader = csv.reader(open(_args.candidatefile))
        for n in range(_args.skip_rows):  # default = 0
            skipped = next(reader)  # skip header
            trace(1, 'Skipping row in CSV file: {}', skipped)
        col_acc = _args.col_acc
        for row in reader:
            idnum = row[col_acc]
            if not idnum:
                continue
            add_one_id(idnum)

    if notinmodes:
        trace(1, '{} accession numbers skipped, not in Modes.', notinmodes)
    return candidate_set


def main():
    # x.normalized extracts the first entry in the namedtuple Obj_id.
    # valid_idnums is a set of all the IDs in the XML file
    valid_idnums = set([x.normalized for x in list_objects(_args.modesfile)])
    numneeded = 0
    if _args.candidatefile:
        candidate_set = build_candidate_set(valid_idnums)
    else:
        candidate_set = valid_idnums
    img_dict = dict()
    build_img_dict(img_dict, _args.imgdir)
    for nid in sorted(candidate_set):
        denid = denormalize_id(nid)
        if _args.invert:
            if nid not in img_dict:
                trace(2, 'Not in image folder: {}', denid)
                continue
        else:
            if nid in img_dict:
                trace(2, 'In image folder: {}', denid)
                if reportfile:
                    print(denid, img_dict[nid][1], file=reportfile)
                continue
        # print IDs of objects needed as they are not in the image folder(s).
        # if --invert is set, print the objects in the image folder(s).
        print(denid, file=outfile)
        numneeded += 1
    needq = f'{"not " if _args.invert else ""}needed'
    trace(1, f'Total {needq}: {numneeded} of {len(candidate_set)} candidates.')


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs()
    if _args.verbose < 2:
        sys.tracebacklimit = 0
    if _args.outfile:
        outfile = open(_args.outfile, 'w')
    else:
        outfile = sys.stdout
    VERBOSE = _args.verbose
    reportfile = open(_args.reportfile, 'w') if _args.reportfile else None
    main()
