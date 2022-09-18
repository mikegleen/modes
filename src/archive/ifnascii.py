"""
Scan a file and report occurrances of non-ASCII bytes.
"""
import sys

infile = open(sys.argv[1], 'rb')
nline = 0
nbyte = 0
for line in infile:
    nline += 1
    nrow = 0
    for c in line:
        nrow += 1
        nbyte += 1
        if c > 0x7F:
            print(nline, nrow, hex(nrow), nbyte, hex(nbyte), c, hex(c))
            # break
print(nline)
