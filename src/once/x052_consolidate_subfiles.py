"""
    Input is a folder containing sub-folders, each of which contains files.
    Output is a folder containing the files from the subfolders.

    Only image files are copied
"""
import os
import shutil
import sys

DRYRUN = False
IMGFILES = ('.jpg', '.jpeg', '.png')


def main():
    filenames = {}
    ncopied = ndups = 0
    for subdir in sorted(os.listdir(indir)):
        subdirpath = os.path.join(indir, subdir)
        if not os.path.isdir(subdirpath):
            if subdir != '.DS_Store':
                print(f'Skipping not folder: {subdir}')
            continue
        for filename in os.listdir(subdirpath):
            _, suffix = os.path.splitext(filename)
            if suffix.lower() not in IMGFILES:
                if filename != '.DS_Store':
                    print(f'Skipping not image: {filename}')
                continue
            if filename in filenames:
                oldsize = os.path.getsize(os.path.join(filenames[filename], filename))
                newsize = os.path.getsize(os.path.join(subdirpath, filename))
                oldfolder = filenames[filename].split('/')[-1]
                newfolder = subdirpath.split('/')[-1]
                print(f'dup found: {filename}, old: {oldfolder}[{oldsize}] '
                      f'new: {newfolder}[{newsize}]')
                if newsize > oldsize:
                    if not DRYRUN:
                        shutil.copy2(os.path.join(subdirpath, filename), outdir)
                    print('...replacing old with larger new.')
                elif newsize == oldsize:
                    print('...identical.')
                else:
                    print('...not replacing.')
                filenames[filename] = subdirpath
                ndups += 1
            else:
                filenames[filename] = subdirpath
                if not DRYRUN:
                    shutil.copy2(os.path.join(subdirpath, filename), outdir)
                ncopied += 1
    print(f'{ncopied=}, {ndups=}')


if __name__ == '__main__':
    assert sys.version_info >= (3, 11)
    indir = sys.argv[1]
    outdir = sys.argv[2]
    main()
    if DRYRUN:
        print('Dry run. Nothing copied.')
