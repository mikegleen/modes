"""
    Delete JPEG files from the website collection database. No parameters
    are required.
"""
from ftplib import FTP

HOST = 'heathrobinsonmuseum.org'
USER = 'mike@heathrobinsonmuseum.org'
PASSWORDFILE = 'etc/passwd'

if __name__ == '__main__':
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
