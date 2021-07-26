"""
    Delete JPEG files from the website collection database.

    The files in the sending directory are of the form: <accession #>.jpg
    Add a prefix of "collection_" to each file.
    Send the file to the host.
    Move the file to the SENT directory.
"""
from ftplib import FTP
import os

HOST = 'heathrobinsonmuseum.org'
USER = 'mike@heathrobinsonmuseum.org'
PASSWORD = 'thegleenster-123?!'
session = FTP(HOST, USER, PASSWORD)

hostdir = session.mlsd()

for fname, _ in hostdir:
    if fname.startswith('collection_'):
        print(f'Deleting {fname}')
        session.delete(fname)
