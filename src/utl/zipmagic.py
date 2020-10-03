"""
    If a file is a zip file, assume it contains exactly one member file.
    If not a zip file, open the file as normal.
"""

import magic  # package python-magic
from zipfile import ZipFile


def openfile(filename, mode='r'):
    if magic.from_file(filename).lower().startswith('zip'):
        myzip = ZipFile(filename)
        names = myzip.namelist()
        file = myzip.open(names[0], mode)
    else:
        file = open(filename, mode)
    return file
