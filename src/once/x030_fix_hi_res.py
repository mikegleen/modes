"""
    Rename files: SH103 Turkish Bath 001.jpg -> SH103.jpg
"""
import os.path
import re
import sys

indir = sys.argv[1]
files = os.listdir(indir)

PATTERN = r'(SH\d+)\w*(.*)\d{3}?\.tif'

for fn in files:
    m = re.match(PATTERN, fn)
    if not m:
        print(f'Skipping: {fn}', file=sys.stderr)
        continue
    # newfn = f'{m.group(1)}.jpg'
    # src = os.path.join(indir, fn)
    # dst = os.path.join(indir, newfn)
    # print(f'{src}, {dst}')
    # os.rename(src, dst)
    print(f'{m.group(1)},{m.group(2).strip()}')
