"""
    Rename files in a directory: JBxxx_title.jpg -> JBxxx.jpg
"""
import os.path
import sys
indir = sys.argv[1]

files = os.listdir(indir)

for fn in files:
    if '_' not in fn or not fn.lower().endswith('.jpg'):
        print(f'filename doesn\'t parse: {fn}')
        continue
    prefix = fn.split('_')[0]
    _, ext = os.path.splitext(fn)
    src = os.path.join(indir, fn)
    dst = os.path.join(indir, prefix + ext)
    print(f'{src}, {dst}')
    os.rename(src, dst)
