# -*- coding: utf-8 -*-
"""

"""
import argparse
import codecs
import copy
import csv
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import Config, Stmt, Cmd
from utl.normalize import modesdatefrombritishdate, sphinxify


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def next_accnum(accnum: str):
    """
    :param accnum: An accession number like LDHRM.2021.2
    :return: The accession number with the trailing index incremented after
             each call.
    """
    if not accnum:
        raise ValueError('None is not a valid argument to next_accnum.')
    mat = re.match(r'(.+?)(\d+$)', accnum)
    prefix = mat.group(1)
    suffix = int(mat.group(2))
    while True:
        yield prefix + str(suffix)
        suffix += 1


def new_subelt(doc, template):
    elt = None
    if Stmt.PARENT_PATH in doc:
        parent = template.find(doc[Stmt.PARENT_PATH])
        if parent is None:
            trace(1, 'Cannot find parent of {}, column {}',
                  doc[Stmt.XPATH], doc[Stmt.TITLE])
        else:
            elt = ET.SubElement(parent, doc[Stmt.TITLE])
    return elt


def main():
    global nrows
    if not _args.noprolog:
        outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    root = ET.parse(templatefile)
    # print('root', root)
    # Assume that the template is really an Interchange file with empty
    # elements.
    object_template = root.find('Object')
    if object_template is None:
        # Ok, so maybe it really is a template
        object_template = root.find('./template/Object')
        if object_template is None:
            raise ValueError('Cannot find the Object element from root or'
                             'from ./template/Object')
    reader = csv.DictReader(incsvfile)
    trace(1, 'CSV Column Headings: {}', reader.fieldnames)
    nrows = 0
    accnumgen = next_accnum(_args.acc_num)  # not used if --acc_num is not set
    for row in reader:
        emit = True
        template = copy.deepcopy(object_template)
        elt = template.find('./ObjectIdentity/Number')
        if _args.acc_num:
            accnum = next(accnumgen)
            trace(2, 'Serial generated: {}', accnum)
        else:
            accnum = row[_args.serial]
        elt.text = accnum
        for doc in config.col_docs:
            # print(doc[Stmt.TITLE], doc[Stmt.XPATH])
            elt = template.find(doc[Stmt.XPATH])
            if elt is None:
                elt = new_subelt(doc, template)
            if elt is None:
                trace(0, 'Cannot create new {}.\nCheck parent_path statement.',
                      doc[Stmt.XPATH])
                sys.exit()
            if doc[Stmt.CMD] == Cmd.CONSTANT:
                elt.text = doc[Stmt.VALUE]
                continue
            text = row[doc[Stmt.TITLE]]
            if Stmt.REQUIRED in doc and not text:
                print(f'*** Required column “{doc[Stmt.TITLE]}” is missing from'
                      f' {accnum}. Object excluded.')
                emit = False
            elt.text = text
            if Stmt.DATE in doc:
                # Only britishdate supported now
                try:
                    elt.text, _, _ = modesdatefrombritishdate(elt.text)
                    # print(type(elt.text))
                except ValueError:
                    elt.text = 'unknown'
        if emit:
            nrows += 1
            outfile.write(ET.tostring(template))
    if not _args.noprolog:
        outfile.write(b'</Interchange>')


def getparser():
    parser = argparse.ArgumentParser(description=sphinxify('''
        Read a CSV file containing two or more columns. The first column
        is the index and the following columns are the field(s) defined by the
        XPATH statement in the config file. Create an
        XML file with data from the CSV file based on a template of the
        XML structure.
        
        The CSV file must have a heading.
        The heading of the column containing the serial number must be 'Serial'
        or an alternative set by --serial parameter. Subsequent columns
        must match the corresponding title in the configuration file. The
        config file may contain only "column" or "constant" commands.
        ''', calledfromsphinx))
    parser.add_argument('--acc_num', help='''
        This is the first accession number in a series to assign to rows
        in the input CSV file. If specified, the column in the CSV file
        containing a serial number, if one exists, is ignored. For example,
        if the parameter is "LDHRM.2021.2", the numbers assigned will be
        "LDHRM.2021.2", "LDHRM.2021.3", etc. This value will be stored in the
        ObjectIdentity/Number element.''')
    parser.add_argument('-i', '--incsvfile', help='''
        The CSV file containing data to be inserted into the XML template.''')
    parser.add_argument('-t', '--templatefile', help='''
        The XML Object template.''')
    parser.add_argument('-o', '--outfile', help='''
        The output XML file.''')
    parser.add_argument('-c', '--cfgfile', required=True,
                        type=argparse.FileType('r'), help='''
        The YAML file describing the column path(s) to update''')
    parser.add_argument('-p', '--noprolog', action='store_true', help='''
        Inhibit the insertion of an XML prolog at the front of the file and an
        <Interchange> element as the root. This results in an invalid XML file
        but is useful if the output is to be manually edited.''')
    parser.add_argument('--serial', default='Serial',
                        help=sphinxify('''
        The column containing the serial number must have a heading with this
        value. This is ignored if the --acc_num parameter is specified.''',
                                       calledfromsphinx))
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
        if doc[Stmt.CMD] not in (Cmd.COLUMN, Cmd.CONSTANT):
            print(f'Command "{doc[Stmt.CMD]}" not allowed, exiting')
            errs += 1
    for doc in c.ctrl_docs:
        print(f'Command "{doc[Stmt.CMD]}" not allowed, exiting.')
        errs += 1
    return errs


calledfromsphinx = True


if __name__ == '__main__':
    global nrows
    assert sys.version_info >= (3, 6)
    calledfromsphinx = False
    _args = getargs(sys.argv)
    templatefile = open(_args.templatefile)
    incsvfile = codecs.open(_args.incsvfile, 'r', encoding='utf-8-sig')
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}', _args.incsvfile)
    trace(1, 'Creating file: {}', _args.outfile)
    config: Config = Config(_args.cfgfile, title=True, dump=_args.verbose > 1,
                            allow_required=True)
    if errors := check_cfg(config):
        trace(1, '{} errors found. Aborting.', errors)
        sys.exit(1)
    main()
    trace(1, 'End csv2xml. {} object{} written.', nrows,
          '' if nrows == 1 else 's')
