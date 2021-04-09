"""
    Rename files in a directory: JBxxx_title.jpg -> JBxxx.jpg
"""
import os.path
INDIR = '/Volumes/Transcend/Downloads/hrmalt/accessioned_medium_res'

files = os.listdir(INDIR)

for fn in files:
    prefix = fn.split('_')[0]
    _, ext = os.path.splitext(fn)
    src = os.path.join(INDIR, fn)
    dst = os.path.join(INDIR, prefix + ext)
    print(f'{src}, {dst}')
    os.rename(src, dst)