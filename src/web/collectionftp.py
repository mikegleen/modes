"""
    Transfer JPEG files to the website collection staging directory.

    The files in the sending directory are of the form: <accession #>.jpg
    Add a prefix of "collection_" to each file.
    Send the file to the host.
    Move the file to the SENT directory.
"""
from ftplib import FTP
import os.path
import shutil

HOST = 'heathrobinsonmuseum.org'
USER = 'mike@heathrobinsonmuseum.org'
PASSWORD = 'thegleenster-123?!'
STAGING_DIR = '/Users/mlg/pyprj/hrm/collection_staging'
SENT_DIR = '/Users/mlg/pyprj/hrm/collection_sent'
VERBOSE = 2


def trace(level, template, *args):
    if VERBOSE >= level:
        print(template.format(*args))


files = os.listdir(STAGING_DIR)
os.chdir(STAGING_DIR)
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
    srcfile = os.path.join(STAGING_DIR, filename)
    dstfile = os.path.join(SENT_DIR, filename)
    shutil.move(srcfile, dstfile)
