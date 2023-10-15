"""
    Input is a folder containing sub-folders, each of which contains files.
    Output is a folder containing the files from the subfolders.

    Only image files are copied
"""
import os
import shutil
import sys


IMGFILES = ('.jpg', '.jpeg', '.png')


def main():
    indir = sys.argv[1]
    for subdir in os.listdir(indir):
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
            shutil.copy2(os.path.join(subdirpath, filename), outdir)


if __name__ == '__main__':
    assert sys.version_info >= (3, 11)
    outdir = sys.argv[2]
    main()
