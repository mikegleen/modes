"""
    For each file in a directory, remove the prefix "collection_".
"""
import os.path
import sys
import time

FILENAME_PREFIX = 'collection_'
VERBOSE = 2


def trace(level, template, *args):
    if VERBOSE >= level:
        print(template.format(*args))


data_dir = sys.argv[1]
files = os.listdir(data_dir)
os.chdir(data_dir)

nfiles = len(files)
trace(1, '{} files to examine.', nfiles)
nupdated = 0
t1 = time.perf_counter()
for filename in files:
    if filename.startswith('.'):
        continue
    if filename.startswith(FILENAME_PREFIX):
        newfilename = filename.removeprefix(FILENAME_PREFIX)
        os.rename(filename, newfilename)
        nupdated += 1
elapsed = time.perf_counter() - t1
print(f'{elapsed:.3f} seconds to update {nupdated} file{"" if nupdated == 1 else "s"}')
