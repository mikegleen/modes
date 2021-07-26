"""
    Rename files: Brinsmead LDHRM2019_018.jpg -> LDHRM.2019.18.jpg
"""
import os.path
import re
import sys

indir = sys.argv[1]
files = os.listdir(indir)

for fn in files:
    m = re.match(r'Brinsmead LDHRM2019_(\d+)\.jpg', fn)
    if not m:
        print(f'Skipping: {fn}')
        continue
    seq = int(m.group(1))  # remove leading zeroes
    newfn = f'LDHRM.2019.{seq}.jpg'
    src = os.path.join(indir, fn)
    dst = os.path.join(indir, newfn)
    print(f'{src}, {dst}')
    os.rename(src, dst)
