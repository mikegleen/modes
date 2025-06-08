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
from colorama import Fore, Style
import codecs
import csv
import sys
import time
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import Cmd, Stmt, yaml_fieldnames, expand_idnum
from utl.cfgutil import Config
from utl.readers import read_include_dict
from utl.excel_cols import col2num
from utl.normalize import normalize_id, denormalize_id, DEFAULT_MDA_CODE
from utl.normalize import if_not_sphinx
from utl.zipmagic import openfile


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args), file=_logfile)


def opencsvwriter(filename, delimiter):
    encoding = 'utf-8-sig' if _args.bom else 'utf-8'
    csvfile = codecs.open(filename, 'w', encoding)
    outcsv = csv.writer(csvfile, delimiter=delimiter, lineterminator=_args.lineterminator)
    trace(1, 'Output: {}', filename)
    return outcsv, csvfile


def one_document(document, parent):
    command = document[Stmt.CMD]
    eltstr = document.get(Stmt.XPATH)
    text = None
    if eltstr:
        element = parent.find(eltstr)
    else:
        element = None
    if element is None and command != Cmd.CONSTANT:
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
        delimiter = document[Stmt.MULTIPLE_DELIMITER]
        # print(f'{elements=}')
        # for e in elements:
        #     print(f'{e.text=}')
        text = delimiter.join([e.text for e in elements if e.text is not None])
    elif command == Cmd.CONSTANT:
        text = document[Stmt.VALUE]
    elif element.text is None:
        text = ''
    else:
        text = element.text.strip()
    if Stmt.NORMALIZE in document:
        text = normalize_id(text, _args.mdacode)
    if Stmt.WIDTH in document:
        text = text[:int(document[Stmt.WIDTH])]
    return text, command


def main(argv):  # can be called either by __main__ or test_xml2csv
    global _args, _logfile
    _args = getargs(argv)
    trace(1, 'Begin xml2csv.', color=Fore.GREEN)
    infilename = _args.infile
    outfilename = _args.outfile
    cfgfilename = _args.cfgfile
    if _args.logfile:
        _logfile = open(_args.logfile, 'w')
    else:
        _logfile = sys.stdout
    infile = openfile(infilename)
    nlines = notfound = nwritten = 0
    Config.reset_config()  # needed by test_xml2csv
    if cfgfilename:
        cfgfile = open(cfgfilename)
    else:
        cfgfile = None
        trace(1, 'Warning: Config file omitted. Only accession numbers will be output.')
    config = Config(cfgfile, dump=_args.verbose >= 2, logfile=_logfile,
                    verbos=_args.verbose)
    outcsv, outfile = opencsvwriter(outfilename, config.delimiter)
    outlist = []
    titles = yaml_fieldnames(config)
    trace(1, 'Columns: {}', ', '.join(titles))
    if _args.heading:
        outcsv.writerow(titles)
    else:
        trace(1, 'Heading row not written.')
    if _args.object:
        expanded = [normalize_id(obj) for obj in expand_idnum(_args.object)]
        includeset = set(expanded)  # JB001-002 -> JB001, JB002
        includes = dict.fromkeys(includeset)
    else:
        includes = read_include_dict(_args.include, _args.include_column,
                                     _args.include_skip, _args.verbose,
                                     logfile=_logfile,
                                     allow_blanks=_args.allow_blanks)
    normids = {}
    objectlevel = 0
    for event, elem in ET.iterparse(infile, events=('start', 'end')):
        # print(event)
        if event == 'start':
            # print(elem.tag)
            if elem.tag == config.record_tag:
                objectlevel += 1
            continue
        # It's an "end" event.
        if elem.tag != config.record_tag:  # default: Object
            continue
        objectlevel -= 1
        if objectlevel:
            continue  # It's not a top level Object.
        data = []
        idelem = elem.find(config.record_id_xpath)
        idnum = idelem.text if idelem is not None else ''
        trace(3, 'idnum: {}', idnum)
        nlines += 1

        norm_idnum = normalize_id(idnum, _args.mdacode, verbose=_args.verbose)
        if norm_idnum in normids:
            print(f'Duplicate id: {norm_idnum}. Old id: {normids[norm_idnum]},'
                  f' New id: {idnum}')
            print('Program aborted.')
            sys.exit(-1)
        normids[norm_idnum] = idnum
        writerow = config.select(elem, includes, exclude=_args.exclude)
        # print(f'{writerow=}')
        if not writerow:
            continue
        # We have selected the id but only write the row if there is something
        # to display. There will always be at least the ID number in the first
        # column unless skip_number was specified in the config.
        if config.skip_number:
            writerow = False
        else:
            # Insert the ID number as the first column.
            data.append(norm_idnum)

        for document in config.col_docs:
            text, command = one_document(document, elem)
            # print(f'{command=}')
            if text is None:
                notfound += 1
                trace(2, '{}: cmd: {}, "{}" is not found in XML.', idnum, command,
                      document[Stmt.TITLE])
                text = ''
            if text:
                writerow = True
            data.append(text)

        if writerow:
            nwritten += 1
            outlist.append(data)
            trace(3, '{} written.', idnum)
        elem.clear()
        if includes and not _args.exclude:
            includes.pop(norm_idnum)
        if _args.short:
            break
    if config.sort_numeric:
        outlist.sort(key=lambda x: int(x[0]))
    else:
        outlist.sort()
    # Create a list of flags indicating whether the value needs to be
    # de-normalized.
    denorm = []
    if not config.skip_number:
        denorm.append(True)  # for the Serial number
    for doc in config.col_docs:
        denorm.append(Stmt.DENORMALIZE in doc)
    lennorm = len(denorm)
    for row in outlist:
        for n, cell in enumerate(row[:lennorm]):
            if denorm[n]:
                row[n] = denormalize_id(cell, _args.mdacode)
        outcsv.writerow(row)
    infile.close()
    if cfgfile:
        cfgfile.close()
    outfile.close()
    if includes and len(includes):
        trace(1, '{} items in include list not in XML.', len(includes))
        if _args.verbose > 0:
            print('In include list but not xml:', file=_logfile)
            for accnum in sorted(includes):
                print(denormalize_id(accnum), file=_logfile)
    if not _args.bom:
        trace(1, 'BOM not written.')
    return nlines, nwritten, notfound


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
    parser.add_argument('--allow_blanks', action='store_true', help='''
    Skip rows in the include CSV file with blank accession numbers. If not
    set, this will cause an abort.
    ''')
    parser.add_argument('-b', '--bom', action='store_true', help='''
        Select this option to insert a byte order mark (BOM) at the front of
        the output CSV file. Use this option when the CSV file is to be
        imported into Excel so that the proper character set (UTF-8) is used.
        ''')
    parser.add_argument('-c', '--cfgfile', help='''
        The config file describing the column_paths to extract. If omitted,
        only the accession numbers will be output.''')
    parser.add_argument('-f', '--force', action='store_true', help='''
        Write output even if none of the columns is populated.''')
    parser.add_argument('--heading', action='store_true', help='''
        Write a row at the front of the CSV file containing the field names.
        These are defined by the "title" statements in the config or inferred
        from the xpath. The first column will contain the accession number
        and the heading will be "Serial".''')
    parser.add_argument('--include', required=False, help='''
        A CSV file specifying the accession numbers of objects to be processed.
        If omitted, all records will be processed. In either case, objects will
        be output based on configuration statements. ''')
    parser.add_argument('--include_column', required=False,
                        default='0', type=str, help='''
        The column number containing the accession number in the file
        specified by the --include option.
        The column can be a number or a spreadsheet-style letter.''' +
                        if_not_sphinx(f''' The default is 0, the first column.''',
                                      calledfromsphinx))

    parser.add_argument('--include_skip', type=int, default=0, help='''
        The number of rows to skip at the front of the include file.''' +
                        if_not_sphinx(f''' The default is 0.
        ''', calledfromsphinx))
    parser.add_argument('-j', '--object', help='''
    Specify a single object to be processed. Do not also specify the include
    file. The argument can be an object range, like JB001-2.
    ''')
    parser.add_argument('-l', '--logfile', help='''
    Specify a file to write messages to. Default is sys.stdout ''')
    parser.add_argument('-m', '--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code, used in normalizing the accession number.''' +
                        if_not_sphinx(f''' The default is "{DEFAULT_MDA_CODE}". ''',
                                      calledfromsphinx))
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-t', '--lineterminator', help=r'''
    Set the line terminator. The default is "\\r\\n". If the output is to be processed on a Unix-like
    system by a program like sed or awk you may wish to set this to "\\n".''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    parser.add_argument('-x', '--exclude', action='store_true', help='''
        Treat the include list as an exclude list.''')
    # print(argv)
    # print(sys.argv)
    # sys.argv = argv
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    args.include_column = col2num(args.include_column)
    # Set the default here because Sphinx can't display \r\n.
    if args.lineterminator is None:
        args.lineterminator = '\r\n'
    return args


calledfromsphinx = True

if __name__ == '__main__':
    global _args, _logfile
    assert sys.version_info >= (3, 6)
    calledfromsphinx = False
    t1 = time.perf_counter()
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    n_lines, n_written, not_found = main(sys.argv)
    elapsed = time.perf_counter() - t1
    if not_found:
        trace(1, 'Warning: {} elements not found in XML.', not_found)
    trace(1, 'End xml2csv. {}/{} lines written to {}. Elapsed: {:5.2f} seconds.',
          n_written, n_lines, _args.outfile, elapsed, color=Fore.GREEN)
