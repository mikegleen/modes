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
PASSWORDFILE = 'etc/passwd'
with open(PASSWORDFILE) as pwfile:
    password = pwfile.read().strip()
session = FTP(HOST, USER, password)

hostdir = session.mlsd()

ndeletes = 0
for fname, _ in hostdir:
    if fname.startswith('collection_'):
        print(f'Deleting {fname}')
        session.delete(fname)
        ndeletes += 1
print(ndeletes, ' files deleted.')