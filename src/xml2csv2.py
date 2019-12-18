# -*- coding: utf-8 -*-
"""
    Extract fields from an XML file, creating a CSV file with the specified
    fields.

    The first column is hard-coded as './ObjectIdentity/Number'. Subsequent
    column_paths are defined in a YAML file.
"""
import argparse
import codecs
import csv
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import read_yaml_cfg, yaml_fieldnames, Cmd, Stmt, validate_yaml_cfg
from utl.cfgutil import yaml_global
from utl.normalize import normalize_id, denormalize_id


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def opencsvwriter(filename):
    encoding = 'utf-8-sig' if _args.bom else 'utf-8'
    csvfile = codecs.open(filename, 'w', encoding)
    outcsv = csv.writer(csvfile, delimiter=',')
    trace(1, 'Output: {}', filename)
    return outcsv


def main(inf, outf, cfgf):
    global nlines, not_found
    config = read_yaml_cfg(cfgf, title=True, dump=_args.verbose >= 2)
    if not validate_yaml_cfg(config):
        print('Config validation failed. Program aborted.')
        sys.exit(1)
    global_stmts = yaml_global(config)
    inhibit_number = Stmt.INHIBIT_NUMBER in global_stmts
    outcsv = opencsvwriter(outf)
    outlist = []
    titles = yaml_fieldnames(config)
    if inhibit_number:
        titles = titles[1:]  # Get rid of the leading 'Serial' entry
    trace(1, 'Columns: {}', ', '.join(titles))
    if _args.fields:
        outcsv.writerow(titles)
    for event, elem in ET.iterparse(inf):
        if elem.tag != 'Object':
            continue
        writerow = True
        data = []
        idelem = elem.find('./ObjectIdentity/Number')
        idnum = idelem.text if idelem is not None else ''
        trace(3, 'idnum: {}', idnum)
        if not inhibit_number:
            data.append(normalize_id(idnum))
        # config is a list of dicts, one dict per YAML document in the config
        # This maps to the columns in the output CSV file plus a few control commands.
        for document in config:
            command = document[Stmt.CMD]
            if command == Cmd.GLOBAL:
                continue
            eltstr = document.get(Stmt.ELT)
            if eltstr:
                element = elem.find(eltstr)
            else:
                element = None
            if element is None:
                not_found += 1
                # dump_document(document)
                trace(2, '{}: cmd {}, "{}" is not found.', idnum, command,
                      document[Stmt.TITLE])
                if command in Cmd.CONTROL_CMDS:
                    writerow = False
                    break
                data.append('')
                continue
            if command in (Cmd.ATTRIB, Cmd.IFATTRIB):
                attribute = document[Stmt.ATTRIBUTE]
                text = element.get(attribute)
            elif command == Cmd.COUNT:
                count = len(list(elem.findall(eltstr)))
                text = f'{count}'
            elif element.text is None:
                text = ''
            else:
                text = element.text.strip()
            if not text and command in (Cmd.IF, Cmd.IFATTRIB, Cmd.IFCONTAINS,
                                        Cmd.IFEQ):
                writerow = False
                break
            if command in (Cmd.IFEQ, Cmd.IFATTRIB, Cmd.IFCONTAINS):
                value = document[Stmt.VALUE]
                textvalue = text
                if Stmt.CASESENSITIVE not in document:
                    value = value.lower()
                    textvalue = textvalue.lower()
                if command == Cmd.IFCONTAINS and value not in textvalue:
                    writerow = False
                    break
                elif command in (Cmd.IFEQ, Cmd.IFATTRIB) and value != textvalue:
                    writerow = False
                    break
                continue
            if Stmt.NORMALIZE in document:
                # print(idnum, f'"{text}"')
                text = normalize_id(text)
                # print(idnum, f'after: "{text}"')
            if Stmt.WIDTH in document:
                text = text[:document[Stmt.WIDTH]]
            data.append(text)

        if writerow:
            nlines += 1
            outlist.append(data)
        if _args.short:
            break
    outlist.sort()
    # Create a list such that for each column set a flag indicating whether the value
    # needs to be de-normalized.
    norm = []
    if not inhibit_number:
        norm.append(True)  # for the Serial number
    lennorm = len(norm)
    for doc in config:
        if doc[Stmt.CMD] in Cmd.CONTROL_CMDS:
            continue
        norm.append(Stmt.NORMALIZE in doc)
    for row in outlist:
        for n, cell in enumerate(row[:lennorm]):
            if norm[n]:
                row[n] = denormalize_id(cell)
        outcsv.writerow(row)


def getargs():
    parser = argparse.ArgumentParser(description='''
    Extract fields from an XML file, creating a CSV file with the specified
    fields. The first column is hard-coded as './ObjectIdentity/Number'.
    Subsequent column_paths are defined in a YAML file containing "column" statements,
    "elt" statements containg the XPATH of the column to extract and other statements to
    control selection of objects to write to the CSV file.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile',  help='''
        The output CSV file.''')
    parser.add_argument('-f', '--fields', action='store_true', help='''
        Write a row at the front of the CSV file containing the field names.'''
                        )
    parser.add_argument('-b', '--bom', action='store_false', help='''
        Normally a BOM is inserted at the front of the output CSV file. This option
        inhibits that.''')
    parser.add_argument('-c', '--cfgfile', required=False, help='''
        The config file describing the column_paths to extract''')
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
    nlines = 0
    not_found = 0
    infile = open(_args.infile)
    cfgfile = open(_args.cfgfile) if _args.cfgfile else None
    main(infile, _args.outfile, cfgfile)
    trace(1, '{} lines written to {}.', nlines, _args.outfile)
    if not_found:
        trace(1, 'Warning: {} elements not found.', not_found)
