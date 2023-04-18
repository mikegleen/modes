"""
    Rename files: SH103 Turkish Bath 001.jpg -> SH103.jpg
"""
import os.path
import re
import sys

incsv = open(sys.argv[1])
print('Serial')

PATTERN = r'(SH\d+)\w*(.*)\.((tif)|(bmp))'
PATTERN = r'((SH|JB)\d+)\s*((.*?)(\d{3})?)\.(tif|bmp|jpg)'

for row in sorted(incsv):
    # print(f'{fn=}')
    m = re.match(r'(LDHRM\.\d{4}\.\d+)\.jpg', row)
    if m:
        print(m.group(1))
        continue
    m = re.match(PATTERN, row)
    if not m:
        print(f'Skipping: {row}', file=sys.stderr)
        continue
    # newfn = f'{m.group(1)}.jpg'
    # src = os.path.join(indir, fn)
    # dst = os.path.join(indir, newfn)
    # print(f'{src}, {dst}')
    # os.rename(src, dst)
    # print(f'{m.group(1)},{m.group(5).strip()}')
    # print(f'{m.group(1)},{m.group(5)}')
    print(m.group(1))
