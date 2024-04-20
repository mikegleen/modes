"""
    For each file in a directory, remove the prefix "collection_".
    For each object, make one file in the format of a thumbnail.
    If there are multiple files for an object like multiple pages or front and
    back scans, only keep the first one.

    Convert the format like "JB1202-001.jpg" to "JB1202.1.jpg".

"""
import os.path
import re
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
        matched = True
        while True:
            m = re.fullmatch(r'JB\d+[AB]?.jpg', newfilename)
            if m:
                # simple case: filename is same as accession id.
                break
            m = re.fullmatch(r'((JB)|(SH)\d+[AB]?-)(\d{3})([AB]).jpg', newfilename)
            if m:
                if not m.group(3):  # if no A or B
                    subnum = int(m.group(2))
                    newfilename = f'{m.group(1)}.{subnum}.jpg'
                    break
                # not numeric so is two-sided page
                if m.group(3) == 'A':
                    subnum = int(m.group(2))
                    newfilename = f'{m.group(1)}.{subnum}.jpg'
                else:
                    match = False  # discard the 'B' side
                    break
            # test for multiple sheets
            m = re.fullmatch(r'(JB\d+[AB]?-)(?P<subnum>\d{3})-(?P<pagenum>\d+)(?P<side>[AB]).jpg', newfilename)
            if m:
                if m.group('pagenum') == '1':
                    if not m.group('side') or m.group('side') == 'A':
                        subnum = int(m.group('subnum'))
                        newfilename = f'{m.group(1)}.{subnum}.jpg'
                        break
                match = False  # discard all but the first page
                break

        os.rename(filename, newfilename)
        nupdated += 1
elapsed = time.perf_counter() - t1
print(f'{elapsed:.3f} seconds to update {nupdated} file{"" if nupdated == 1 else "s"}')
