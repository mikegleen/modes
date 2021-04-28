"""

"""
import os.path
INDIR = '/Volumes/Transcend/Downloads/hrmalt/accessioned_WW1'

files = os.listdir(INDIR)

for fn in files:
    if '_' not in fn:
        continue
    prefix = fn.split('_')[0]
    print(prefix)