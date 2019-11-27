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
    cols = read_yaml_cfg(cfgf)
    if not validate_yaml_cfg(cols):
        print('Config validation failed. Program aborted.')
        sys.exit(1)
    outcsv = opencsvwriter(outf)
    outlist = []
    targets = yaml_fieldnames(cols)
    trace(1, 'Columns: {}', ', '.join(targets))
    if _args.fields:
        outcsv.writerow(targets)
    for event, elem in ET.iterparse(inf):
        if elem.tag != 'Object':
            continue
        writerow = True
        # data[0] = Id
        data = [elem.find('./ObjectIdentity/Number').text]
        # cols is a list of dicts, one dict per YAML document in the config
        # This maps to the columns in the output CSV file plus a few control commands.
        for col in cols:
            text = ''
            attribute = None
            command = col[Stmt.CMD]
            elt = col[Stmt.ELT]
            element = elem.find(elt)
            if element is None:
                not_found += 1
                trace(2, '"{}" is not found.', elt)
            if command in (Cmd.ATTRIB, Cmd.IFATTRIB):
                attribute = col.get(Stmt.ATTRIBUTE)
            if attribute and element is not None:
                text = element.get(attribute)
            elif command == 'count':
                count = len(list(elem.findall(elt)))
                text = f'{count}'
            elif element is None or element.text is None:
                text = ''
            else:
                text = element.text.strip()
            if not text and command == Cmd.IF:
                writerow = False
                break
            if command in (Cmd.IFEQ, Cmd.IFATTRIB):
                value = col[Stmt.VALUE]
                textvalue = text
                if Stmt.CASESENSITIVE not in col:
                    value = value.lower()
                    textvalue = textvalue.lower()
                if value != textvalue:
                    writerow = False
                    break
                continue

            data.append(text)
        if writerow:
            nlines += 1
            outlist.append(data)
        if _args.short:
            break
    outlist.sort()
    for row in outlist:
        outcsv.writerow(row)


def getargs():
    parser = argparse.ArgumentParser(description='''
    Extract fields from an XML file, creating a CSV file with the specified
    fields. The first column is hard-coded as './ObjectIdentity/Number'.
    Subsequent column_paths are defined in a DSL file containing "column" statements
    each with one parameter, the XPATH of the column to extract.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile',  help='''
        The output CSV file.''')
    parser.add_argument('-f', '--fields', action='store_true', help='''
        Write a row at the front of the CSV file containing the field names.'''
                        )
    parser.add_argument('-b', '--bom', action='store_true', help='''
        Insert a BOM at the front of the output CSV file.''')
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
