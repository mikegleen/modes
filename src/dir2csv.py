"""
    Read a directory of JPEG files and create a CSV file with one column
    containing the filename minus the trailing .jpg
    A heading row of 'Serial' precedes the data.
"""
import os.path
import re
import sys

if len(sys.argv) != 3:
    print('Parameters: input folder, output csv')
    sys.exit()
indir = sys.argv[1]
outfile = open(sys.argv[2], 'w')

files = os.listdir(indir)
nout = 0
print('Serial', file=outfile)
for fn in files:
    m = re.match(r'(collection_)?(.+)\.jpg', fn)
    if not m:
        print(f'Skipping: {fn}')
        continue
    print(m.group(2), file=outfile)
    nout += 1
print(f'{nout} rows written.')