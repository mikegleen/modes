# -*- coding: utf-8 -*-
"""
    Extract fields from an XML file, creating a CSV file with the specified
    fields.

    The default first column is hard-coded as './ObjectIdentity/Number'.
    Subsequent column_paths are defined in a YAML file. See cfgutil.py for
    a description of the YAML file.
"""
import argparse
import codecs
import csv
import sys
import time
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import Cmd, Stmt, yaml_fieldnames
from utl.cfgutil import Config, select
from utl.normalize import normalize_id, denormalize_id


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def opencsvwriter(filename, delimiter):
    encoding = 'utf-8' if _args.nobom else 'utf-8-sig'
    csvfile = codecs.open(filename, 'w', encoding)
    outcsv = csv.writer(csvfile, delimiter=delimiter)
    trace(1, 'Output: {}', filename)
    return outcsv, csvfile


def one_document(document, parent):
    command = document[Stmt.CMD]
    eltstr = document.get(Stmt.XPATH)
    if eltstr:
        element = parent.find(eltstr)
    else:
        element = None
    if element is None:
        return None, command
    if command == Cmd.ATTRIB:
        attribute = document[Stmt.ATTRIBUTE]
        text = element.get(attribute)
    elif command == Cmd.COUNT:
        count = len(list(parent.findall(eltstr)))
        text = f'{count}'
    elif element.text is None:
        text = ''
    else:
        text = element.text.strip()
    if Stmt.NORMALIZE in document:
        text = normalize_id(text)
    if Stmt.WIDTH in document:
        text = text[:document[Stmt.WIDTH]]
    return text, command


def main(argv):  # can be called either by __main__ or test_xml2csv
    global _args
    _args = getargs(argv)
    infilename = _args.infile
    outfilename = _args.outfile
    cfgfilename = _args.cfgfile
    infile = open(infilename)
    cfgfile = open(cfgfilename)
    nlines = notfound = 0
    Config.reset_config()  # needed by test_xml2csv
    config = Config(cfgfile, title=True, dump=_args.verbose >= 2)
    outcsv, outfile = opencsvwriter(outfilename, config.delimiter)
    outlist = []
    titles = yaml_fieldnames(config)
    trace(1, 'Columns: {}', ', '.join(titles))
    if _args.heading:
        outcsv.writerow(titles)
    objectlevel = 0
    for event, elem in ET.iterparse(infile, events=('start', 'end')):
        # print(event)
        if event == 'start':
            # print(elem.tag)
            if elem.tag == config.record_tag:
                objectlevel += 1
            continue
        # It's an "end" event.
        if elem.tag != config.record_tag:
            continue
        objectlevel -= 1
        if objectlevel:
            continue  # It's not a top level Object.
        data = []
        idelem = elem.find(config.record_id_xpath)
        idnum = idelem.text if idelem is not None else ''
        trace(3, 'idnum: {}', idnum)

        writerow = select(elem, config)
        if not writerow:
            continue
        if not config.skip_number:
            data.append(normalize_id(idnum, _args.verbose))

        for document in config.col_docs:
            text, command = one_document(document, elem)
            if text is None:
                notfound += 1
                trace(2, '{}: cmd {}, "{}" is not found.', idnum, command,
                      document[Stmt.TITLE])
                text = ''
            data.append(text)

        nlines += 1
        outlist.append(data)
        elem.clear()
        if _args.short:
            break
    outlist.sort()
    # Create a list of flags indicating whether the value needs to be
    # de-normalized.
    norm = []
    if not config.skip_number:
        norm.append(True)  # for the Serial number
    for doc in config.col_docs:
        if doc[Stmt.CMD] in Cmd.get_control_cmds():
            continue
        norm.append(Stmt.NORMALIZE in doc)
    lennorm = len(norm)
    for row in outlist:
        for n, cell in enumerate(row[:lennorm]):
            if norm[n]:
                row[n] = denormalize_id(cell)
        outcsv.writerow(row)
    infile.close()
    cfgfile.close()
    outfile.close()
    return nlines, notfound


def getargs(argv=None):
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
    parser.add_argument('-b', '--nobom', action='store_true', help='''
        Normally a BOM is inserted at the front of the output CSV file. This option
        inhibits that.''')
    parser.add_argument('-c', '--cfgfile', required=False, help='''
        The config file describing the column_paths to extract'''
                        )
    parser.add_argument('--heading', action='store_true', help='''
        Write a row at the front of the CSV file containing the field names.'''
                        )
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    # print(argv)
    # print(sys.argv)
    # sys.argv = argv
    args = parser.parse_args(args=argv[1:])
    return args


if __name__ == '__main__':
    global _args
    assert sys.version_info >= (3, 6)
    t1 = time.perf_counter()
    n_lines, not_found = main(sys.argv)
    elapsed = time.perf_counter() - t1
    trace(1, '{} lines written to {}. Elapsed: {:5.2f} seconds.', n_lines,
          _args.outfile, elapsed)
    if not_found:
        trace(1, 'Warning: {} elements not found.', not_found)
