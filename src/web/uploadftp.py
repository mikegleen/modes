"""
    Transfer JPEG files to the website collection staging directory.

    One parameter is required, the directory holding the new images.

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
import sys
import time
from colorama import Fore, Style

HOST = 'heathrobinsonmuseum.org'
USER = 'mike@heathrobinsonmuseum.org'
PASSWORDFILE = 'etc/passwd'
COLLECTION_PREFIX = 'collection_'
VERBOSE = 2
DRYRUN = False


def trace(level, template, *args, color=None):
    if VERBOSE >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


if len(sys.argv) < 2:
    trace(0, 'One parameter required, the directory holding images to upload. Exiting.', color=Fore.RED)
    sys.exit(1)

sending_dir = sys.argv[1]
files = os.listdir(sending_dir)
with open(PASSWORDFILE) as pwfile:
    password = pwfile.read().strip()
os.chdir(sending_dir)
session = FTP(HOST, USER, password)

nfiles = len(files)
trace(1, '{} files to send.', nfiles)
nsent = 0
t1 = time.perf_counter()
for filename in files:
    if filename.startswith('.'):
        trace(1, 'Skipping hidden file {}', filename, color=Fore.YELLOW)
        continue
    if not filename.endswith('.jpg'):
        trace(1, 'Skipping non-jpg {}', filename, color=Fore.YELLOW)
        continue
    if not filename.startswith(COLLECTION_PREFIX):
        prefix, suffix = os.path.splitext(filename)
        prefix = prefix.upper()
        newfilename = COLLECTION_PREFIX + prefix + suffix
        os.rename(filename, newfilename)
        filename = newfilename
    if DRYRUN:
        print(f"Dry Run: {filename=}")
        continue
    file = open(filename, 'rb')
    response = session.storbinary(f'STOR {filename}', file)
    if not response.startswith('226'):
        trace(1, 'Error in {}: {}', filename, response, color=Fore.RED)
    else:
        trace(2, '{}: {}', filename, response)
    file.close()
    nsent += 1
    if nsent % 10 == 0:
        trace(1, '{} of {} sent', nsent, nfiles)
elapsed = time.perf_counter() - t1
trace(1, f'{elapsed:.3f} seconds to send {nsent} file{"" if nsent == 1 else "s"}', color=Fore.GREEN)
