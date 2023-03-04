# -*- coding: utf-8 -*-
"""

    The input is three files, an XML file, a YAML file and a CSV file. The
    XML file is the Modes database file to be updated. The YAML file
    contains definitions for elements to be updated from a CSV file.
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
from colorama import Fore, Style
from datetime import date
import os
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import Config, Stmt, Cmd, new_subelt, expand_idnum
from utl.normalize import normalize_id, sphinxify, denormalize_id
from utl.normalize import if_not_sphinx, DEFAULT_MDA_CODE
from utl.normalize import modes_person, modesdatefrombritishdate
import utl.normalize as nd
from utl.readers import row_dict_reader


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def loadnewvals(allow_blanks=False):
    newval_dict = {}
    reader = row_dict_reader(_args.mapfile, _args.verbose, _args.skip_rows)
    for row in reader:
        # print(f'{row=}')
        accnum = row[_args.serial]
        if not accnum:
            if allow_blanks:
                trace(2, 'Row with blank accession number skipped: {}', row)
                continue  # skip blank accession numbers
            else:
                raise ValueError('Blank accession number in include file;'
                                 ' --allow_blank not selected.')
        if cfg.add_mda_code and accnum[0].isnumeric():
            accnum = _args.mdacode + '.' + accnum
        accnums = expand_idnum(accnum)
        trace(3, 'accnums = {}', accnums)
        for accnum in accnums:
            newval_dict[normalize_id(accnum)] = row
    return newval_dict


def one_element(objelem, idnum):
    """
    Update the fields specified by "column" configuration documents.
    Do not overwrite existing values unless --replace is specified.

    Note that we have already tested that idnum is in newvals.

    :param objelem: the Object
    :param idnum: the ObjectIdentity/Number text
    :return: True if updated, False otherwise
    """
    global nupdated, nunchanged, nequal
    updated = False
    for doc in cfg.col_docs:
        command = doc[Stmt.CMD]
        xpath = doc[Stmt.XPATH]
        title = doc[Stmt.TITLE]
        if command == Cmd.DELETE:
            parent = objelem.find(doc[Stmt.PARENT_PATH])
            target = objelem.find(xpath)
            if target is not None:
                trace(2, 'Removing {}', xpath)
                parent.remove(target)
            continue
        elif command == Cmd.DELETE_ALL:
            targets = objelem.findall(xpath)
            if targets is not None:
                for target in targets:
                    objelem.remove(target)
            continue
        if command == Cmd.CONSTANT:
            newtext = doc[Stmt.VALUE]
        else:  # command is COLUMN
            # get the text from the CSV column for this row
            newtext = newvals[idnum][doc[Stmt.TITLE]]
        if not newtext and not (_args.empty or command == Cmd.CONSTANT):
            trace(3, '{}: empty field in CSV ignored. --empty not specified',
                  idnum)
            continue
        target = objelem.find(xpath)
        if target is None:
            target = new_subelt(doc, objelem, idnum, _args.verbose)
            if target is None:  # parent is not specified or doesn't exist
                trace(1, '{}: Cannot find target "{}"', idnum, xpath)
                continue
        oldtext = target.text
        if oldtext and not _args.replace:
            if oldtext != newtext:
                trace(1, '{} {} Unchanged, old text: "{}",'
                         ' new text: "{}"\nSet --replace to force update.',
                      denormalize_id(idnum), title, oldtext, newtext)
            nunchanged += 1
            continue
        if oldtext and oldtext == newtext:
            nequal += 1
            trace(2, '{} {}: Unchanged: "{}" == "{}"', idnum, title,
                  oldtext, newtext)
            continue
        if newtext == '{{clear}}':
            newtext = ''
        elif newtext == '{{today}}':
            newtext = _args.date
        trace(3, '{} {}: Updated: "{}" -> "{}"', idnum, title, oldtext,
              newtext)
        if Stmt.NORMALIZE in doc:
            newtext = denormalize_id(newtext)
        elif Stmt.DATE in doc:
            # Only britishdate supported now
            try:
                newtext, _, _ = modesdatefrombritishdate(newtext)
                # print(type(elt.text))
            except ValueError:
                newtext = 'unknown'
        elif Stmt.PERSON_NAME in doc:
            newtext = modes_person(newtext)
        target.text = newtext
        updated = True
        nupdated += 1
    return updated


def main():
    global nwritten
    outfile.write(b'<?xml version="1.0" encoding="UTF-8"?><Interchange>\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find(cfg.record_id_xpath)
        idnum = idelem.text if idelem is not None else None
        nidnum = normalize_id(idnum)
        trace(3, 'idnum: {}', idnum)
        if nidnum and nidnum in newvals:
            updated = one_element(elem, nidnum)
            del newvals[nidnum.upper()]
        else:
            updated = False
            if _args.missing:
                trace(2, 'Not in CSV file: "{}"', idnum)
        if updated or _args.all:
            outfile.write(ET.tostring(elem, encoding='utf-8'))
            nwritten += 1
        if _args.short:
            break
    outfile.write(b'</Interchange>')
    for nidnum in newvals:
        trace(1, 'In CSV but not XML: "{}"', denormalize_id(nidnum))


def getparser():
    parser = argparse.ArgumentParser(description='''
        Read a CSV file containing two or more column_paths. The first column
        is the index and the following columns are the field(s) defined by the
        XPATH statement in the YAML configuration file. Update the
        XML file with data from the CSV file. The CSV file must contain
        a heading row with column titles matching the ``title`` statements
        in the YAML configuration file.''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects. The default is to only write updated objects.''')
    parser.add_argument('--allow_blanks', action='store_true', help='''
        Skip rows in the include CSV file with blank accession numbers. If not
        set, this will cause an abort. ''')
    parser.add_argument('-c', '--cfgfile', required=True,
                        type=argparse.FileType('r'), help='''
        Required. The YAML configuration file describing the column path(s) to
         update''')
    parser.add_argument('-d', '--date', help='''
        If a column in the CSV file contains '{{today}}', use this value for
        the field text. The default is today’s date.
        ''')
    parser.add_argument('-e', '--empty', action='store_true', help=sphinxify('''
        Normally, an empty field in the CSV file means that no action is to be
        taken. If -e is selected, empty values from the CSV will overwrite
        the fields in the file. Another way to do this for specific fields is
        to set the text to ``{{clear}}`` in the CSV field to be emptied.
        --empty implies --replace.''', called_from_sphinx))
    parser.add_argument('--missing', action='store_true', help='''
        By default, ignore indices missing from the CSV file. If selected,
        trace the missing index. Useful if you are updating all objects.''')
    parser.add_argument('-m', '--mapfile', required=True, help=sphinxify('''
        Required. The CSV file mapping the object number to the new element
        value(s). The file may also be an Excel spreadsheet with a filename
        ending ``.xlsx``. The
        first column must contain the object number and subsequent columns
        must have headers that correspond to the titles of the columns in the
        configuration
        file. If a row in the CSV file has fewer fields than defined in the
        configuration file, zero-length strings will be assumed. See
        --empty.''', called_from_sphinx))
    parser.add_argument('--mdacode', default=DEFAULT_MDA_CODE,
                        help=sphinxify(f'''
        Specify the MDA code, used if the accession number in the CSV file
        is specified without the leading MDA code. You must also specify
        the global statement ``add_mda_code`` in the YAML config file.''',
                                       called_from_sphinx) +
                        if_not_sphinx(''' The default is "{DEFAULT_MDA_CODE}".
                        ''', called_from_sphinx))
    parser.add_argument('-r', '--replace', action='store_true', help=sphinxify('''
        Replace existing values. If not specified only empty elements will be
        updated. Existing values will be cleared if the value in the CSV file
        contains the special value ``{{clear}}``. See also --empty. If
        --replace is not set a warning will be issued if the existing value
        is not blank.''', called_from_sphinx))
    parser.add_argument('--serial', default='Serial', help=sphinxify('''
        The column containing the serial number must have a heading with this
        value. ''' + if_not_sphinx('''
        The default value is "Serial".''', called_from_sphinx),
                                                         called_from_sphinx))
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('--skip_rows', type=int, default=0, help=sphinxify('''
        Skip rows at the beginning of the CSV file specified by --mapfile.
        ''', called_from_sphinx))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if args.empty:
        args.replace = True
    if os.path.splitext(args.mapfile)[1].lower() not in ('.csv', '.xlsx'):
        raise ValueError('mapfile must be a CSV or Excel file.')
    if args.date:
        args.date, _, _ = nd.modesdatefrombritishdate(args.date)
    else:
        args.date = nd.modesdate(date.today())
    return args


def check_cfg(config: Config):
    errs = 0
    for doc in config.col_docs:
        cmd = doc[Stmt.CMD]
        if cmd == Cmd.DELETE:
            for stmt in doc:
                # Note some statements are created internally if they are not
                # explicitly specified in the config.
                if stmt not in (Stmt.CMD, Stmt.XPATH, Stmt.TITLE,
                                Stmt.MULTIPLE_DELIMITER, Stmt.PARENT_PATH,
                                Stmt.ELEMENT):
                    trace(1, 'Delete command: Statement "{}" not allowed, '
                             'ignored', stmt, color=Fore.RED)
                    errs += 1
        elif cmd not in (Cmd.COLUMN, Cmd.CONSTANT):
            trace(1, 'Command "{}" not allowed, ignored', cmd, color=Fore.RED)
            errs += 1
        elif (Stmt.ATTRIBUTE in doc) ^ (Stmt.ATTRIBUTE_VALUE in doc):
            trace(1, 'cmd: {}: attribute statement requires '
                  'attribute_value:', cmd, color=Fore.RED)
            errs += 1
    for doc in config.ctrl_docs:  # "global" is not in this dict
        trace(1, 'Command "{}" not allowed, ignored.', doc[Stmt.CMD],
              color=Fore.RED)
        errs += 1
    return errs


def sq(val):
    return '' if val == 1 else 's'


called_from_sphinx = True
if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    called_from_sphinx = False
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    nupdated = nunchanged = nwritten = nequal = 0
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}\nCreating file: {}', _args.infile, _args.outfile)
    cfg = Config(_args.cfgfile, dump=_args.verbose > 1)
    if errors := check_cfg(cfg):
        trace(1, '{} command{} ignored.', errors, 's' if errors > 1 else '')
        trace(1, 'update_from_csv aborting due to config error(s).',
              color=Fore.RED)
        sys.exit(1)
    newvals = loadnewvals(allow_blanks=_args.allow_blanks)
    nnewvals = len(newvals)
    main()
    trace(1, '{} element{} in {} object{} updated.\n'
          '{} existing element{} unchanged.\n'
          '{} element{} updated where new == old.',
          nupdated, sq(nupdated),
          nnewvals, sq(nnewvals),
          nunchanged, sq(nunchanged),
          nequal, sq(nequal))
    trace(1, 'End update_from_csv. {} objects written.', nwritten,
          color=Fore.GREEN)
