# -*- coding: utf-8 -*-
"""
    Merge the template files in a folder to a single file.

"""
import argparse
from inspect import getframeinfo, stack
import os.path
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from colorama import Fore, Style


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if _args.verbose > 1:
            caller = getframeinfo(stack()[1][0])
            print(f'{os.path.basename(caller.filename)} line {caller.lineno}: ', end='')
        if color:
            if len(args) == 0:
                print(f'{color}{template}{Style.RESET_ALL}')
            else:
                print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            if len(args) == 0:
                print(template)
            else:
                print(template.format(*args))


def main():
    declaration = f'<templates application="Object">'
    outfile.write(bytes(declaration, encoding=_args.encoding))
    files = os.listdir(_args.indir)
    for filename in files:
        if not filename.lower().endswith('.xml'):
            continue
        infile = open(os.path.join(_args.indir, filename))
        roottree = ET.parse(infile)
        templates = roottree.getroot()
        if templates.tag != 'templates':
            print(f'Unexpected root tag: {templates.tag} in file {filename}')
            sys.exit(1)
        for template in templates.findall('./template'):
            outfile.write(ET.tostring(template, encoding=_args.encoding))
            template.clear()
        templates.clear()
        infile.close()

    outfile.write(b'</templates>')


def getargs():
    parser = argparse.ArgumentParser(description='''
    Merge the template files in a folder to a single file.
        ''')
    parser.add_argument('-i', '--indir', required=True, help='''
        The folder containing the input XML template files.''')
    parser.add_argument('-o', '--outfile', help='''
        The output XML file.''')
    parser.add_argument('-e', '--encoding', default='utf-8', help='''
        Set the output encoding. The default is "utf-8".
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 13)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs()
    trace(1, "Begin {}.", os.path.basename(sys.argv[0]), color=Fore.GREEN)
    outfile = open(_args.outfile, 'wb')
    main()
    trace(1, "End {}.", os.path.basename(sys.argv[0]), color=Fore.GREEN)
