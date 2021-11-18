"""
    For each file in a directory of type jpg or png, open that file in
    preview.app

    The purpose of this is to allow rotation of the file.
"""
import os.path
import subprocess
import sys


def main():
    targetdir = sys.argv[1]

    try:
        targetlist = os.listdir(targetdir)
        numtargets = len(targetlist)
        ntarg = 0
        for target in targetlist:
            ntarg += 1
            print(f'file {ntarg} of {numtargets}')
            filename, extension = os.path.splitext(target)
            if extension.lower() in ('.jpg', '.png'):
                subprocess.run(['open', '-W', os.path.join(targetdir, target)])
            else:
                print('skipping', target)
    except KeyboardInterrupt:
        print('\nExiting.')
        sys.exit(1)


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    main()
