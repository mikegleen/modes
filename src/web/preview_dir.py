"""
    For each file in a directory of type jpg or png, open that file in
    preview.app

    The purpose of this is to allow rotation of the file.
"""
import os.path
import subprocess
import sys
from utl.normalize import normalize_id
import time


def main():
    targetdir = sys.argv[1]

    try:
        targetlist = [(normalize_id(os.path.splitext(t)[0], strict=False), t)
                      for t in os.listdir(targetdir)]
        targetlist = sorted(targetlist, key=lambda item: item[0])
        numtargets = len(targetlist)
        ntarg = 0
        for _, target in targetlist:
            time.sleep(0.05)
            ntarg += 1
            print(f'file {ntarg} of {numtargets}: {target}')
            filename, extension = os.path.splitext(target)
            if extension.lower() in ('.jpg', '.jpeg', '.png'):
                subprocess.run(['open', '-W', os.path.join(targetdir, target)])
            else:
                print('skipping', target)
    except KeyboardInterrupt:
        print('\nExiting.')
        sys.exit(1)


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    main()
