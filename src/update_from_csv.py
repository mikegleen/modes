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
from utl.normalize import normalize_id, sphinxify, denormalize_id


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def new_subelt(doc, root):
    elt = None
    if Stmt.PARENT_PATH in doc:
        # print(f'{doc[Stmt.PARENT_PATH]}')
        parent = root.find(doc[Stmt.PARENT_PATH])
        title = doc[Stmt.TITLE]
        if parent is None:
            trace(1, 'Cannot find parent of {}, column {}',
                  doc[Stmt.XPATH], title)
        elif ' ' in title:
            trace(1, 'Cannot create title with embedded spaces: {}', title)
        else:
            elt = ET.SubElement(parent, title)
    return elt


def loadnewvals(allow_blanks=False):
    """
    Read the CSV file containing objectid -> new element values
    :param allow_blanks: if True, rows with a blank accession number are
            skipped. Otherwise a ValueError exception is raised.
    :return: the dictionary containing the mappings where the key is the
             objectid and the value is a list of the remaining columns
    """
    newval_dict = {}
    with codecs.open(_args.mapfile, 'r', 'utf-8-sig') as mapfile:
        reader = csv.reader(mapfile)
        skiprows = _args.skip_rows
        for n in range(skiprows):  # default = 0
            skipped = next(reader)  # skip header
            if _args.verbose >= 1:
                print(f'Skipping row in map file: {skipped}')
        if _args.heading:
            # Check that the first row in the CSV file contains the same
            # column headings as in the title statements of the YAML file.
            row = next(reader)
            row = [r.strip() for r in row]
            irow = iter(row)
            next(irow)  # skip Serial column
            for doc in cfg.col_docs:
                col = next(irow)
                title = doc[Stmt.TITLE]
                if col.lower() != title.lower():
                    print(f'Mismatch on heading: "{title}" in config !='
                          f' "{col}" in CSV file')
                    sys.exit(1)

        for row in reader:
            row = [r.strip() for r in row]
            idnum = row[0]
            if not idnum:
                if allow_blanks:
                    trace(2, 'Row with blank accession number skipped: {}', row)
                    continue  # skip blank accession numbers
                else:
                    raise ValueError('Blank accession number in include file;'
                                     ' --allow_blank not selected.')
            # Strip off the accession number in the first column so that the
            # list matches the columns in the config file. Note that this
            # depends on the accession number being in the first column.
            newval_dict[normalize_id(idnum)] = row[1:]
    return newval_dict


def one_element(elem, idnum):
    """
    Update the fields specified by "column" configuration documents.
    Do not overwrite existing values unless --replace is specified.

    Note that we have already tested that idnum is in newvals.

    :param elem: the Object
    :param idnum: the ObjectIdentity/Number text
    :return: True if updated, False otherwise
    """
    global nupdated, nunchanged, nequal
    updated = False
    inewtexts = iter(newvals[idnum])  # we've already checked that it's there
    for doc in cfg.col_docs:
        command = doc[Stmt.CMD]
        xpath = doc[Stmt.XPATH]
        title = doc[Stmt.TITLE]
        if command == Cmd.CONSTANT:
            newtext = doc[Stmt.VALUE]
        else:  # command is COLUMN
            try:
                newtext = next(inewtexts)
            except StopIteration:
                newtext = ""
                trace(2, '{}: short line in CSV file', idnum)
            if xpath.lower() == Stmt.FILLER:
                continue
        if not newtext and not _args.empty:
            trace(3, '{}: empty field in CSV ignored. --empty not specified',
                  idnum)
            continue
        target = elem.find(xpath)
        if target is None and newtext:
            target = new_subelt(doc, elem)
            if target is None:  # parent is not specified or doesn't exist
                trace(1, '{}: Cannot find target "{}"', idnum, xpath)
                continue
        oldtext = target.text
        if not oldtext or _args.replace:
            if oldtext and oldtext == newtext:
                nequal += 1
                trace(2, '{} {}: Unchanged: "{}" == "{}"',idnum, title, oldtext, newtext)
                continue
            else:
                if newtext == '{{clear}}':
                    newtext = ''
                trace(2, '{} {}: Updated: "{}" -> "{}"', idnum, title, oldtext, newtext)
                target.text = newtext
                updated = True
                nupdated += 1
        else:
            trace(2, '{} {}: Unchanged, --replace not set: "{}" (new text = "{}")',
                  idnum, title, oldtext, newtext)
            nunchanged += 1
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
        XML file with data from the CSV file.
        If a row in the CSV file has fewer columns than the number of
        columns specified in the YAML file, replace the text with an empty
        string.''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects. The default is to only write updated objects.''')
    parser.add_argument('--allow_blanks', action='store_true', help='''
        Skip rows in the include CSV file with blank accession numbers. If not
        set, this will cause an abort.
        ''')
    parser.add_argument('-c', '--cfgfile', required=True,
                        type=argparse.FileType('r'), help='''
        The YAML file describing the column path(s) to update''')
    parser.add_argument('-e', '--empty', action='store_true', help=sphinxify('''
        Normally, an empty field in the CSV file means that no action is to be
        taken. If -e is selected, empty values from the CSV will overwrite
        the fields in the file. Another way to do this for specific fields is
        to set the text to ``{{clear}}`` in the CSV field to be emptied.
        --empty implies --replace.''', called_from_sphinx))
    parser.add_argument('--missing', action='store_true', help='''
        By default, ignore indices missing from the CSV file. If selected,
        trace the missing index.''')
    parser.add_argument('--heading', action='store_true', help='''
        The first row of the map file contains a heading which must match the
        value of the title statement in the corresponding column document
        (case insensitive).''')
    parser.add_argument('-m', '--mapfile', required=True, help='''
        The CSV file mapping the object number to the new element value(s).''')
    parser.add_argument('-r', '--replace', action='store_true', help='''
        Replace existing values. If not specified only empty elements will be
        updated. Existing values will be cleared if the value in the CSV file
        contains the special value ``{{clear}}``. See also --empty.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('--skip_rows', type=int, default=0, help='''
        Skip rows at the beginning of the CSV file.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if args.empty:
        args.replace = True
    return args


def check_cfg(c):
    errs = 0
    for doc in c.col_docs:
        if doc[Stmt.CMD] not in (Cmd.COLUMN, Cmd.CONSTANT):
            print(f'Command "{doc[Stmt.CMD]}" not allowed, ignored')
            errs += 1
    for doc in c.ctrl_docs:
        print(f'Command "{doc[Stmt.CMD]}" not allowed, ignored.')
        errs += 1
    return errs


def sq(val):
    return '' if val == 1 else 's'


called_from_sphinx = True


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    called_from_sphinx = False
    _args = getargs(sys.argv)
    nupdated = nunchanged = nwritten = nequal = 0
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}\nCreating file: {}', _args.infile, _args.outfile)
    cfg = Config(_args.cfgfile, dump=_args.verbose > 1)
    if errors := check_cfg(cfg):
        trace(1, '{} command{} ignored.', errors, 's' if errors > 1 else '')
        print('update_from_csv aborting due to config error(s).')
        sys.exit(1)
    newvals = loadnewvals(allow_blanks=_args.allow_blanks)
    nnewvals = len(newvals)
    main()
    trace(1, '{} element{} in {} object{} updated.\n'
          '{} existing element{} unchanged.\n'
          '{} element{} where new == old.',
          nupdated, sq(nupdated),
          nnewvals, sq(nnewvals),
          nunchanged, sq(nunchanged),
          nequal, sq(nequal))
    trace(1, 'End update_from_csv. {} objects written.', nwritten)
