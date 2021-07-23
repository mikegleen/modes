"""
    Call this before copying a bunch of files into another directory to see
    what you're gonna hose over.
"""

import os
import sys

dir1 = os.listdir(sys.argv[1])
dir2 = os.listdir(sys.argv[2])

set1 = set()
set2 = set()

for fn in dir1:
    set1.add(fn)

for fn in dir2:
    if fn in set1:
        print(f'dup: {fn}')
