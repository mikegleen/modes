# -*- coding: utf-8 -*-
"""

"""
import argparse
import codecs
import csv
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import read_yaml_cfg, Cmd, Stmt


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
        for row in reader:
            newval_dict[row[0].strip()] = [val.strip() for val in row[1:]]
    return newval_dict


def one_element(elem, idnum):
    """
    If the location in the newlocs dictionary is different from the location
    in the XML, update the XML.
    Note that we have already tested that idnum is in newvals.

    :param elem: the Object
    :param idnum: the ObjectIdentity/Number text
    :return: None
    """
    updated = False
    inewtexts = iter(newvals[idnum])  # we've already checked that it's there
    for doc in cfg:
        try:
            newtext = next(inewtexts)
        except StopIteration:
            trace(1, '{}: short line in CSV file', idnum)
            return
        if not newtext:
            trace(2, '{}: empty cell in CSV file', idnum)
            continue
        target = elem.find(doc[Stmt.XPATH])
        if target is None:
            trace(1, "{}: Cannot find target '{}'", idnum, doc[Stmt.XPATH])
            return
        text = target.text
        if text != newtext or _args.all:
            trace(2, '{}: Updated: "{}" -> "{}"', idnum, text, newtext)
            target.text = newtext
            updated = True
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
        updated = False
        if idnum and idnum in newvals:
            updated = one_element(elem, idnum)
            del newvals[idnum]
        elif _args.warn:
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
    Update Object records from a CSV file. The element or elements to update are defined
    in a YAML file containing column commands. The column commands will correspond to the
    columns in the CSV file, starting with the second column. The first column must
    contain the ID of the object to be updated.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects and, if -w is selected, issue a warning if an object is not in
        the detail CSV file. The default is to only write updated objects. In either case
        warn if an object in the CSV file is not in the input XML file.
        ''')
    parser.add_argument('-c', '--cfgfile', required=True,
                        type=argparse.FileType('r'), help='''
        The YAML file describing the element xpaths to update''')
    parser.add_argument('-f', '--force', action='store_true', help='''
        Replace existing values. If not specified only empty elements will be
        inserted. ''')
    parser.add_argument('-m', '--mapfile', required=True, help='''
        The CSV file mapping the object number to the new element value.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-w', '--warn', action='store_true', help='''
        Valid if -a is selected. Warn if an object in the XML file is not in the CSV file.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    cfg = read_yaml_cfg(_args.cfgfile)
    badcfg = False
    for document in cfg:
        if document[Stmt.CMD] != Cmd.COLUMN:
            trace(1, 'Error: cmd: {} not supported. Only "column" command allowed.',
                  document[Stmt.CMD])
            badcfg = True
    if badcfg:
        trace(1, 'No output created.')
        sys.exit(1)
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    newvals = loadnewvals()
    main()
    trace(1, 'End update2.')
