"""
    Transfer JPEG files to the website collection staging directory.

    The files in the sending directory are of the form: <accession #>.jpg
    This program will:
        Add a prefix of "collection_" to each file, if needed.
        Send the file to the host.

    This script is like collectionftp.py except that instead of a hard-coded
    SENDING folder, a folder is named as a parameter. The sent files remain in
    the named folder.
"""
from ftplib import FTP
import os.path
import shutil
import sys

HOST = 'heathrobinsonmuseum.org'
USER = 'mike@heathrobinsonmuseum.org'
PASSWORD = 'thegleenster-123?!'
VERBOSE = 2


def trace(level, template, *args):
    if VERBOSE >= level:
        print(template.format(*args))


sending_dir = sys.argv[1]
files = os.listdir(sending_dir)
os.chdir(sending_dir)
session = FTP(HOST, USER, PASSWORD)

nfiles = len(files)
trace(1, '{} files to send.', nfiles)
nsent = 0
for filename in files:
    if filename.startswith('.'):
        continue
    if not filename.startswith('collection_'):
        newfilename = 'collection_' + filename
        os.rename(filename, newfilename)
        filename = newfilename
    file = open(filename, 'rb')
    response = session.storbinary(f'STOR {filename}', file)
    if not response.startswith('226'):
        trace(1, 'Error in {}: {}', filename, response)
    else:
        trace(2, '{}: {}', filename, response)
    file.close()
    nsent += 1
    if nsent % 10 == 0:
        trace(1, '{} of {} sent', nsent, nfiles)
