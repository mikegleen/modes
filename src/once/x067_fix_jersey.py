"""
    Rename files: SH103 Turkish Bath 001.jpg -> SH103.jpg
"""
import os.path
import re
import sys

indir = sys.argv[1]
files = os.listdir(indir)
print('Serial')

PATTERN = r'((SH|JB)\d+)\s*((.*?)(\d{3})?)\.(tif|bmp|jpg)'

for fn in sorted(files):
    # print(f'{fn=}')
    if not fn.endswith('.tif'):
        continue
    newfn, _ = fn.split(maxsplit=1)
    newfn += '.tif'
    src = os.path.join(indir, fn)
    dst = os.path.join(indir, newfn)
    # print(f'{src}, {dst}')
    os.rename(src, dst)
    print(f'{fn} -> {newfn}')
