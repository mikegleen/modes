# -*- coding: utf-8 -*-
"""
    Extract fields from an XML file, creating a CSV file with the specified
    fields.

    The default first column is the accession id, initially set to
    './ObjectIdentity/Number' but can be changed in the YAML config.
    Subsequent column_paths are defined in a YAML file. See README.md for
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
from utl.cfgutil import Config, read_include_list
from utl.normalize import normalize_id, denormalize_id, DEFAULT_MDA_CODE
from utl.zipmagic import openfile


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def opencsvwriter(filename, delimiter):
    encoding = 'utf-8-sig' if _args.bom else 'utf-8'
    csvfile = codecs.open(filename, 'w', encoding)
    outcsv = csv.writer(csvfile, delimiter=delimiter)
    trace(1, 'Output: {}', filename)
    return outcsv, csvfile


def one_document(document, parent, config: Config):
    command = document[Stmt.CMD]
    eltstr = document.get(Stmt.XPATH)
    text = None
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
    elif command == Cmd.KEYWORD:
        value = document[Stmt.VALUE]
        if element.text.strip() == value:
            keyword = element.find('Keyword')
            text = keyword.text.strip()
    elif command == Cmd.MULTIPLE:
        elements = parent.findall(eltstr)
        delimiter = config.multiple_delimiter
        if Stmt.MULTIPLE_DELIMITER in document:
            delimiter = document[Stmt.MULTIPLE_DELIMITER]
        # print(f'{elements=}')
        # for e in elements:
        #     print(f'{e.text=}')
        text = delimiter.join([e.text for e in elements if e.text is not None])
    elif element.text is None:
        text = ''
    else:
        text = element.text.strip()
    if Stmt.NORMALIZE in document:
        text = normalize_id(text, _args.mdacode)
    if Stmt.WIDTH in document:
        text = text[:document[Stmt.WIDTH]]
    return text, command


def main(argv):  # can be called either by __main__ or test_xml2csv
    global _args
    _args = getargs(argv)
    infilename = _args.infile
    outfilename = _args.outfile
    cfgfilename = _args.cfgfile
    infile = openfile(infilename)
    nlines = notfound = 0
    Config.reset_config()  # needed by test_xml2csv
    if cfgfilename:
        cfgfile = open(cfgfilename)
    else:
        cfgfile = None
        trace(1, 'Warning: Config file omitted. Only accession numbers will be output.')
    config = Config(cfgfile, title=True, dump=_args.verbose >= 2)
    outcsv, outfile = opencsvwriter(outfilename, config.delimiter)
    outlist = []
    titles = yaml_fieldnames(config)
    trace(1, 'Columns: {}', ', '.join(titles))
    if not _args.heading:
        trace(1, 'Heading row not written.')
    if _args.heading:
        outcsv.writerow(titles)
    objectlevel = 0
    includes = read_include_list(_args.include, _args.include_column,
                                 _args.include_skip, _args.verbose)
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

        writerow = config.select(elem, includes)
        if not writerow:
            continue
        if includes:
            includes.remove(idnum.upper())
        if not config.skip_number:
            # Insert the ID number as the first column.
            data.append(normalize_id(idnum, _args.mdacode, verbose=_args.verbose))

        for document in config.col_docs:
            text, command = one_document(document, elem, config)
            if text is None:
                notfound += 1
                trace(2, '{}: cmd: {}, "{}" is not found in XML.', idnum, command,
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
                row[n] = denormalize_id(cell, _args.mdacode)
        outcsv.writerow(row)
    infile.close()
    if cfgfile:
        cfgfile.close()
    outfile.close()
    if includes and len(includes):
        if _args.verbose == 1:
            print(f'{len(includes)} items in include list not in XML.')
        if _args.verbose > 1:
            print('In include list but not xml:')
            for accnum in includes:
                print(accnum)
    if not _args.bom:
        trace(1, 'BOM not written.')
    return nlines, notfound


def getparser():  # called either by getargs or sphinx
    parser = argparse.ArgumentParser(description='''
    Extract fields from an XML file, creating a CSV file with the specified
    fields. See the README file for details about the configuration file.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes. This can be the original xml file or
        a zipped file.''')
    parser.add_argument('outfile',  help='''
        The output CSV file.''')
    parser.add_argument('-b', '--bom', action='store_true', help='''
        Select this option to insert a BOM at the front of the output CSV file.
        Use this option when the CSV file is to be imported into Excel so that
        the proper character set (UTF-8) is used.
        ''')
    parser.add_argument('-c', '--cfgfile', required=True, help='''
        The config file describing the column_paths to extract. If omitted,
        only the accession numbers will be output.''')
    parser.add_argument('--heading', action='store_true', help='''
        Write a row at the front of the CSV file containing the field names.
        These are defined by the "title" statements in the config or inferred
        from the xpath.''')
    parser.add_argument('--include', required=False, help='''
        A CSV file specifying the accession numbers of objects to be processed.
        If omitted, all records will be processed. In either case, objects will
        be output based on configuration statements.''')
    parser.add_argument('--include_column', required=False, type=int,
                        default=0, help='''
        The column number containing the accession number in the file
        specified by the --include option. The default is 0, the first column.
        ''')
    parser.add_argument('--include_skip', type=int, default=1, help='''
        The number of rows to skip at the front of the include file. The
        default is 1, usually the heading.
        ''')
    parser.add_argument('-m', '--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code, used in normalizing the accession number.
        The default is "{DEFAULT_MDA_CODE}". ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    # print(argv)
    # print(sys.argv)
    # sys.argv = argv
    return parser


def getargs(argv):
    parser = getparser()
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
        trace(1, 'Warning: {} elements not found in XML.', not_found)
