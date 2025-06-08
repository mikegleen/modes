"""
    For each file in a directory, remove the prefix "collection_".
"""
import argparse
from colorama import Fore, Style
import os.path
import sys
import time

import utl.normalize as nd

COLLECTION_PREFIX = 'collection_'
IMGFILES = ('.jpg', '.jpeg', '.png')


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def getparser():
    parser = argparse.ArgumentParser(description=nd.sphinxify('''
    Specify one of the functions defined by the positional parameters.
        ''', called_from_sphinx))
    parser.add_argument('command', choices=['add', 'remove'], help='''
        The function to perform to either add or remove a prefix to filenames.
        The valid file types are: ''' + str(IMGFILES))
    parser.add_argument('filepath',  help='''
        Either a directory name or a single file.''')
    parser.add_argument('-p', '--prefix', default=COLLECTION_PREFIX,
                        help='''Set the prefix to be prepended. ''' +
                             nd.if_not_sphinx('''The default is "''' +
                                              COLLECTION_PREFIX +
                                              '''".
        ''', called_from_sphinx))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


def onefile(filename: str):
    global nupdated
    prefix, suffix = os.path.splitext(filename)
    if suffix.lower() not in IMGFILES:
        trace(1, 'Skipping non-jpg {}', filename, color=Fore.YELLOW)
        return
    match _args.command:
        case 'add':
            if not filename.startswith(COLLECTION_PREFIX):
                prefix = prefix.upper()
                newfilename = COLLECTION_PREFIX + prefix + suffix
                os.rename(filename, newfilename)
                nupdated += 1
        case 'remove':
            if filename.startswith(COLLECTION_PREFIX):
                newfilename = filename.removeprefix(COLLECTION_PREFIX)
                os.rename(filename, newfilename)
                nupdated += 1


def main():
    filepath = _args.filepath
    if os.path.isfile(filepath):
        onefile(filepath)
    elif os.path.isdir(filepath):
        os.chdir(filepath)
        files = os.listdir()
        nfiles = len(files)
        trace(1, '{} files to examine.', nfiles)
        for filename in files:
            if filename.startswith('.'):
                trace(1, 'Skipping hidden file: {}', filename, color=Fore.YELLOW)
                continue
            onefile(filename)


called_from_sphinx = True

if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    t1 = time.perf_counter()
    nupdated = 0
    called_from_sphinx = False
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    main()
    elapsed = time.perf_counter() - t1
    print(f'{elapsed:.3f} seconds to update {nupdated} file{"" if nupdated == 1 else "s"}')
