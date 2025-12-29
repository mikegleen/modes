"""
    Rename files in a directory: xxx.jpeg -> xxx.jpg
    SH68.12.jpg --> SH68.012.jpg
"""
import os.path
import re
import sys


def main():
    indir = sys.argv[1]

    files = os.listdir(indir)

    for fn in files:
        prefix, ext = os.path.splitext(fn)
        m = re.match(r'(SH68\.)(\d+)', prefix)
        if m:
            src = os.path.join(indir, fn)
            newfn = f'{m[1]}{int(m[2]):03}' + ext
            dst = os.path.join(indir, newfn)
            print(f'{src} -> {dst}')
            os.rename(src, dst)

        # if ext.lower() == '.jpeg':
        #     ext = '.jpg'
        #     src = os.path.join(indir, fn)
        #     dst = os.path.join(indir, prefix + ext)
        #     print(f'{src} -> {dst}')
        #     os.rename(src, dst)


if __name__ == '__main__':
    main()
