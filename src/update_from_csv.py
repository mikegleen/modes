# -*- coding: utf-8 -*-
"""

    The input is three files, an XML file, a YAML file and a CSV file. The
    XML file is the Modes database file to be updated. The YAML file
    contains xslt definitions for elements to be updated from a CSV file.
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
    with codecs.open(_args.mapfile, 'r', 'utf-8-sig') as mapfile:
        reader = csv.reader(mapfile)
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


def one_element(elem, idnum):
    """
    Update the fields specified by "column" configuration documents.
    Do not overwrite existing values unless --force is specified.

    Note that we have already tested that idnum is in newvals.

    :param elem: the Object
    :param idnum: the ObjectIdentity/Number text
    :return: True if updated, False otherwise
    """
    global nupdated, nunchanged
    updated = False
    inewtexts = iter(newvals[idnum.upper()])  # we've already checked that it's there
    for doc in cfg.col_docs:
        command = doc[Stmt.CMD]
        if command != Cmd.COLUMN:
            continue  # Don't generate a column
        xpath = doc[Stmt.XPATH]
        try:
            newtext = next(inewtexts)
        except StopIteration:
            newtext = ""
            if not _args.force:
                trace(2, '{}: short line stopped updating. -force not specified',
                      idnum)
        if not newtext and not _args.force:
            trace(2, '{}: empty field in CSV ignored. -force not specified',
                  idnum)
            continue
        target = elem.find(xpath)
        if target is None:
            trace(1, '{}: Cannot find target "{}"', idnum, xpath)
            return updated
        text = target.text
        if not text or _args.force:
            trace(2, '{}: Updated: "{}" -> "{}"', idnum, text, newtext)
            target.text = newtext
            updated = True
            nupdated += 1
        else:
            trace(2, '{}: Unchanged: "{}" (new text = "{}")', idnum, text,
                  newtext)
            nunchanged += 1
    return updated


def main():
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find('./ObjectIdentity/Number')
        idnum = idelem.text if idelem is not None else None
        trace(3, 'idnum: {}', idnum)
        if idnum and idnum in newvals:
            updated = one_element(elem, idnum)
            del newvals[idnum.upper()]
        else:
            updated = False
            if _args.missing:
                trace(2, 'Not in CSV file: "{}"', idnum)
        if updated or _args.all:
            outfile.write(ET.tostring(elem, encoding='us-ascii'))
        if _args.short:
            break
    outfile.write(b'</Interchange>')
    for idnum in newvals:
        trace(1, 'In CSV but not XML: "{}"', idnum)


def getargs():
    parser = argparse.ArgumentParser(description='''
        Read a CSV file containing two or more column_paths. The first column
        is the index and the following columns are the field(s) defined by the
        XPATH statement in the DSL file as defined in xml2csv.py. Update the
        XML file with data from the CSV file.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects. The default is to only write updated objects.''')
    parser.add_argument('-c', '--cfgfile', required=True,
                        type=argparse.FileType('r'), help='''
        The YAML file describing the column path(s) to update''')
    parser.add_argument('-f', '--force', action='store_true', help='''
        Replace existing values. If not specified only empty elements will be
        inserted.
        If a row in the CSV file has fewer columns than the number of
        columns specified in the YAML file, replace the text with an empty
        string. The default is to stop processing that row at that point and
        only update the columns containing data.
        Allow replacing text fields with empty values from the CSV file.
        ''')
    parser.add_argument('--missing', action='store_true', help='''
        By default, ignore indices missing from the CSV file. If selected,
        trace the missing index.''')
    parser.add_argument('--heading', action='store_true', help='''
        The first row of the map file contains a heading which must match the
        value of the title statement in the corresponding column document
        (case insensitive).
        ''')
    parser.add_argument('-m', '--mapfile', required=True, help='''
        The CSV file mapping the object number to the new element value(s).''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


def check_cfg(c):
    errs = 0
    for doc in cfg.col_docs:
        if doc[Stmt.CMD] != Cmd.COLUMN:
            print(f'Command "{doc[Stmt.CMD]}" not allowed, exiting')
            errs += 1
    for doc in cfg.ctrl_docs:
        print(f'Command "{doc[Stmt.CMD]}" not allowed, exiting.')
        errs += 1
    return errs


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    nupdated = nunchanged = 0
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Creating file: {}', _args.outfile)
    cfg = Config(_args.cfgfile, title=True, dump=_args.verbose > 1)
    errors = check_cfg(cfg)
    if errors:
        print(f'{errors} errors found. Aborting.')
        sys.exit(1)
    newvals = loadnewvals()
    nnewvals = len(newvals)
    trace(1, 'Input file: {}', _args.infile)
    main()
    trace(1, 'End update_from_csv. {}/{} object{} updated. {} existing'
          ' element{} unchanged.', nupdated, nnewvals,
          '' if nupdated == 1 else 's', nunchanged,
          '' if nunchanged == 1 else 's')
