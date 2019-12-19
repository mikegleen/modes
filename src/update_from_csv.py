# -*- coding: utf-8 -*-
"""
    The input is two files, a YAML file and a CSV file.
    The YAML file contains xslt definitions for elements to be updated from a
    CSV file. The format of the CSV file is that the first column contains a
    serial number and subsequent columns contain the values to be inserted into
    the corresponding elements.

    The YAML file contains multiple documents, separated by lines containing
    "---"; each document corresponds to an element to be updated. The documents
    may contain "title" statements. If one document contains a title statement,
    they all must. If title statements are included, then the first row of the
    CSV file contains column titles that must correspond to the titles in the
    YAML file. The test is case-insensitive.

"""
import argparse
import codecs
import csv
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import read_yaml_cfg, Stmt, Cmd


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def loadnewvals():
    """
    Read the CSV file containing objectid -> new element value
    :return: the dictionary containing the mappings
    """
    newval_dict = {}
    with codecs.open(_args.mapfile, 'r', 'utf-8-sig') as mapfile:
        reader = csv.reader(mapfile)
        if _args.heading:
            row = next(reader)
            irow = iter(row)
            next(irow)  # skip Serial
            for doc in cfg:
                if doc[Stmt.CMD] in Cmd.CONTROL_CMDS:
                    continue
                col = next(irow)
                title = doc[Stmt.TITLE]
                if col.lower() != title.lower():
                    print(f'Mismatch on heading: "{title}" in config != {col}'
                          ' in CSV file')
                    sys.exit(1)
        for row in reader:
            newval_dict[row[0].strip()] = [val.strip() for val in row[1:]]
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
    global nupdated
    updated = False
    inewtexts = iter(newvals[idnum])  # we've already checked that it's there
    for doc in cfg:
        command = doc[Stmt.CMD]
        if command in Cmd.CONTROL_CMDS:
            continue  # Don't generate a column
        xpath = doc[Stmt.ELT]
        try:
            newtext = next(inewtexts)
        except StopIteration:
            trace(2, '{}: short line', idnum)
            return updated
        if not newtext:
            continue
        target = elem.find(xpath)
        if target is None:
            trace(1, "{}: Cannot find target '{}'", idnum, xpath)
            return updated
        text = target.text
        if not text or _args.force:
            trace(2, '{}: Updated: "{}" -> "{}"', idnum, text, newtext)
            target.text = newtext
            updated = True
            nupdated += 1
        else:
            trace(2, '{}: Unchanged: {} (new text = {})', idnum, text, newtext)
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
            del newvals[idnum]
        else:
            updated = False
            if not _args.ignore:
                trace(1, 'Not in CSV file: {}', idnum)
        if updated or _args.all:
            outfile.write(ET.tostring(elem, encoding='us-ascii'))
        if _args.short:
            break
    outfile.write(b'</Interchange>')
    for idnum in newvals:
        trace(1, 'In CSV but not XML: {}', idnum)


def getargs():
    parser = argparse.ArgumentParser(description='''
        Read a CSV file containing two column_paths. The first column is the index and
        the second column is the field defined by the XPATH statement in the DSL
        file as defined in xml2csv.py. Update the XML file with data from the
        CSV file.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects. The default is to only write updated objects.''')
    parser.add_argument('-c', '--cfgfile', required=True,
                        type=argparse.FileType('r'), help='''
        The YAML file describing the column_paths to update''')
    parser.add_argument('-f', '--force', action='store_true', help='''
        Replace existing values. If not specified only empty elements will be
        inserted.''')
    parser.add_argument('-g', '--ignore', action='store_true', help='''
        Ignore indices missing from the CSV file. If not selected, trace
        the missing index.''')
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


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    nupdated = 0
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    cfg = read_yaml_cfg(_args.cfgfile, title=True)
    newvals = loadnewvals()
    nnewvals = len(newvals)
    main()
    trace(1, 'End update_from_csv. {}/{} objects updated.', nupdated, nnewvals)
