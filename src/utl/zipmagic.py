"""
    If a file is a zip file, assume it contains exactly one member file.
    If not a zip file, open the file as normal.
"""

import magic  # package python-magic
from zipfile import ZipFile


def openfile(filename, mode='r'):
    # magic.from_file returns a descriptor string like "Zip archive data..."
    if magic.from_file(filename).lower().startswith('zip'):
        myzip = ZipFile(filename)
        names = myzip.namelist()
        # noinspection PyTypeChecker
        file = myzip.open(names[0], mode)
    else:
        file = open(filename, mode)
    return file


if __name__ == '__main__':
    print('This module is not callable.')
