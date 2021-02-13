# -*- coding: utf-8 -*-
"""

    The input is three files, an XML template file, a YAML file and a CSV file.
    The XML template contains one Object record to populate. The YAML file
    contains xslt definitions for elements to be inserted from a CSV file.
    The format of the CSV file is that the first column contains a serial
    number and subsequent columns contain the values to be inserted into the
    corresponding elements. Note that there is no entry in the YAML file
    for the serial number in the CSV file.

    The YAML file contains multiple documents, separated by lines containing
    "---"; each document corresponds to an element to be updated. The following
    example is of a single element to be updated.

        ---
        cmd: column
        xpath: ./ObjectLocation/Reason

    The documents may contain "title" statements. If one document contains a
    title statement, they all must. If title statements are included,
    then the first row of the CSV file contains column titles that must
    correspond to the titles in the YAML file. The test is case-insensitive.
    This feature is invoked by the --heading option.

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


def loadnewvals():
    """
    Read the CSV file containing objectid -> new element values
    :return: the dictionary containing the mappings where the key is the
             objectid and the value is a list of the remaining columns
    """
    newval_dict = {}
    with codecs.open(_args.incsvfile, 'r', 'utf-8-sig') as incsvfile:
        reader = csv.reader(incsvfile)
        if _args.heading:
            # Check that the first row in the CSV file contains the same
            # column headings as in the title statements of the YAML file.
            row = next(reader)
            irow = iter(row)
            next(irow)  # skip Serial column
            for doc in cfg.col_docs:
                col = next(irow)
                title = doc[Stmt.TITLE]
                if col.lower() != title.lower():
                    print(f'Mismatch on heading: "{title}" in config != {col}'
                          ' in CSV file')
                    sys.exit(1)
        for row in reader:
            newval_dict[row[0].strip().upper()] = [val.strip() for val in row[1:]]
    return newval_dict


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


def getargs():
    parser = argparse.ArgumentParser(description='''
        Read a CSV file containing two or more column_paths. The first column
        is the index and the following columns are the field(s) defined by the
        XPATH statement in the DSL file as defined in cfgutil.py. Create an
        XML file with data from the CSV file.
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
    parser.add_argument('--heading', action='store_true', help='''
        The first row of the CSV file contains a heading which must match the
        value of the title statement in the corresponding column document
        (case insensitive).
        ''')
    parser.add_argument('-p', '--prolog', action='store_true', help='''
        Insert an XML prolog at the front of the file and an <Interchange>
        element as the root.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
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
    _args = getargs()
    templatefile = open(_args.templatefile)
    incsvfile = open(_args.incsvfile, newline='', encoding='utf-8-sig')
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
