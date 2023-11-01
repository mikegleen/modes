"""
    Rename files in a directory: xxx.jpeg -> xxx.jpg
"""
import os.path
import sys


def main():
    indir = sys.argv[1]

    files = os.listdir(indir)

    for fn in files:
        prefix, ext = os.path.splitext(fn)
        if ext.lower() == '.jpeg':
            ext = '.jpg'
            src = os.path.join(indir, fn)
            dst = os.path.join(indir, prefix + ext)
            print(f'{src} -> {dst}')
            os.rename(src, dst)


if __name__ == '__main__':
    main()
