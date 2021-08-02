"""
    Rename files: Brinsmead LDHRM2019_018.jpg -> LDHRM.2019.18.jpg
"""
import os.path
import re
import sys

indir = sys.argv[1]
files = os.listdir(indir)

PATTERN = r'LDHRM-2021-(\d+)(.?)\.jpg'

for fn in files:
    m = re.match(PATTERN, fn)
    if not m:
        print(f'Skipping: {fn}')
        continue
    seq = int(m.group(1))  # remove leading zeroes
    suffix = m.group(2)
    newfn = f'LDHRM.2021.{seq}{suffix}.jpg'
    src = os.path.join(indir, fn)
    dst = os.path.join(indir, newfn)
    print(f'{src}, {dst}')
    os.rename(src, dst)
