# -*- coding: utf-8 -*-
"""

"""
import argparse
import codecs
import copy
import csv
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import Config, Stmt, Cmd


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def main():
    global nrows
    if _args.prolog:
        outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    root = ET.parse(templatefile)
    # print('root', root)
    # Assume that the template is really an Interchange file with empty
    # elements.
    object_template = root.find('Object')
    if not object_template:
        # Ok, so maybe it really is a template
        object_template = root.find('./template/Object')
    reader = csv.DictReader(incsvfile)
    nrows = 0
    for row in reader:
        template = copy.deepcopy(object_template)
        nrows += 1
        elt = template.find('./ObjectIdentity/Number')
        elt.text = row['Serial']
        for doc in cfg.col_docs:
            # print(doc[Stmt.TITLE], doc[Stmt.XPATH])
            elt = template.find(doc[Stmt.XPATH])
            elt.text = row[doc[Stmt.TITLE]]
        outfile.write(ET.tostring(template))
    if _args.prolog:
        outfile.write(b'</Interchange>')


def getparser():
    parser = argparse.ArgumentParser(description='''
        Read a CSV file containing two or more colums. The first column
        is the index and the following columns are the field(s) defined by the
        XPATH statement in the config file. Create an
        XML file with data from the CSV file based on a template of the
        XML structure.
        
        The first column's heading value must be 'Serial'. Subsequent columns
        must match the corresponding title in the configuration file. The
        config file may contain only "column" commands.
        ''')
    parser.add_argument('incsvfile', help='''
        The CSV file containing data to be inserted into the XML template.''')
    parser.add_argument('templatefile', help='''
        The XML Object template.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-c', '--cfgfile', required=True,
                        type=argparse.FileType('r'), help='''
        The YAML file describing the column path(s) to update''')
    parser.add_argument('-p', '--prolog', action='store_true', help='''
        Insert an XML prolog at the front of the file and an <Interchange>
        element as the root.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


def check_cfg(c):
    """
    Only the column command is allowed.
    :param c: The Config instance
    :return: Nonzero if the config fails.
    """
    errs = 0
    for doc in c.col_docs:
        if doc[Stmt.CMD] != Cmd.COLUMN:
            print(f'Command "{doc[Stmt.CMD]}" not allowed, exiting')
            errs += 1
    for doc in c.ctrl_docs:
        print(f'Command "{doc[Stmt.CMD]}" not allowed, exiting.')
        errs += 1
    return errs


if __name__ == '__main__':
    global nrows
    assert sys.version_info >= (3, 6)
    _args = getargs(sys.argv)
    templatefile = open(_args.templatefile)
    incsvfile = codecs.open(_args.incsvfile, 'r', encoding='utf-8-sig')
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}', _args.incsvfile)
    trace(1, 'Creating file: {}', _args.outfile)
    cfg = Config(_args.cfgfile, title=True, dump=_args.verbose > 1)
    if errors := check_cfg(cfg):
        trace(1, '{errors} errors found. Aborting.', errors)
        sys.exit(1)
    main()
    trace(1, 'End csv2xml. {} object{} created.', nrows,
          '' if nrows == 1 else 's')
