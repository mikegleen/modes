"""
    Walk a tree of scanned files and extract just the full images or the
    stitched images.

    Input is a folder like:

    hrmbox
    └── S24
        ├── JB425.jpg
        ├── SH82
        │   ├── 2022-06-27-0001.jpg
        │   ├── 2022-06-27-0002.jpg
        │   └── SH82.jpg
        └── SH85.jpg

    In the above example, hrmbox is the root folder passed as the input
    argument. S24 is the name of the box containing multiple pictures.
    JB425.jpg is an image of a picture that was scanned in one pass.
    The folder SH82 contains the partial scans with names beginning 2022....
    It also contains the stitched image named SH82.jpg. SH85.jpg is another
    image that was scanned in a single pass.

"""
import os.path
import shutil
import sys


def onebox(box):
    global ncandidates, ncopied
    for filename in os.listdir(box):
        filepath = os.path.join(box, filename)
        ncandidates += 1
        if os.path.isdir(filepath):
            try:
                shutil.copy2(os.path.join(filepath, f'{filename}.jpg'),
                             outdir)
                ncopied += 1
                print('    ', filename, ' copied.')
            except FileNotFoundError as e:
                print(e.filename, e.strerror)
        else:
            try:
                shutil.copy2(filepath, outdir)
                ncopied += 1
            except FileNotFoundError as e:
                print(e.filename, e.strerror)


def harvest():
    print('Begin harvesting {}', inroot)
    for box in os.listdir(inroot):
        print(f'{box=}')
        boxpath = os.path.join(inroot, box)
        if not os.path.isdir(boxpath):
            print(f'Not a directory, skipping: {box}')
            continue
        onebox(boxpath)


calledfromsphinx = True
if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    inroot = sys.argv[1]
    outdir = sys.argv[2]
    if not os.path.isdir(outdir):
        print(outdir, ' is not a directory. Aborting.')
        sys.exit()
    ncandidates = ncopied = 0
    harvest()
    print(f'{ncopied} copied of {ncandidates} candidates')
