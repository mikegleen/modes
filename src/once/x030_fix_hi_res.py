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
    m = re.match(PATTERN, fn)
    if not m:
        print(f'Skipping: {fn}', file=sys.stderr)
        continue
    newfn = f'{m.group(1)}.{m.group(6)}'
    src = os.path.join(indir, fn)
    dst = os.path.join(indir, newfn)
    # print(f'{src}, {dst}')
    os.rename(src, dst)
    print(f'{fn} -> {newfn}')
