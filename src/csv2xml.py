# -*- coding: utf-8 -*-
"""

"""
import argparse
from colorama import Fore
from datetime import date
import copy
import os.path
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


from utl.cfgutil import Config, Stmt, Cmd, new_subelt, process_if_other_column
from utl.normalize import modesdatefrombritishdate, sphinxify, if_not_sphinx
from utl.normalize import DEFAULT_MDA_CODE, normalize_id, denormalize_id
from utl.normalize import modes_person, modesdate
from utl.readers import row_dict_reader
from utl.trace import trace_sub


def trace(level, template, *args, color=None):
    trace_sub(level, _args.verbose, template, color, args)


def clean_accnum(accnum: str):
    """

    :param accnum: input alleged accession number. Remove any leading zeroes
                   and convert back to denormalized form fit for insertion into
                   the XML file
    :return:       denormalized accession number
                   Raises ValueError or AssertionError if the accession number
                   is invalid.
    """
    naccnum = normalize_id(accnum)
    return denormalize_id(naccnum)


def next_accnum(accnum: str):
    """
    :param accnum: An accession number like LDHRM.2021.2
    :return: The accession number with the trailing index incremented after
             each call.
    """
    if not accnum:
        return None
    mat = re.match(r'(.+?)(\d+$)', accnum)
    prefix = mat.group(1)
    suffix = int(mat.group(2))
    while True:
        yield prefix + str(suffix)
        suffix += 1


def create_items(doc, elt, root, text):
    """
    :param doc: the Items document from the config
    :param elt: the element created from the xpath
    :param root: the object element
    :param text: The descriptions joined by the delimiter usually "|"
    :return: None
    """
    olditems = elt.findall('Item')
    for item in olditems:
        elt.remove(item)
    if not text:
        return
    itemtexts = text.split(doc[Stmt.MULTIPLE_DELIMITER])
    itemnumber = 0
    for itemnumber, text in enumerate(itemtexts, start=1):
        item = ET.SubElement(elt, 'Item')
        listnumber = ET.SubElement(item, 'ListNumber')
        listnumber.text = str(itemnumber)
        description = ET.SubElement(item, 'BriefDescription')
        description.text = text
    numberofitems = root.find('NumberOfItems')
    if numberofitems is None:
        numberofitems = ET.SubElement(root, "NumberOfItems")
    numberofitems.text = str(itemnumber)


def get_object_from_file(templatefilepath):
    """
    :param templatefilepath: The path from the --template parameter or the csv
                             file
    :return: the Object element
    """
    with open(templatefilepath) as templatefile:
        root = ET.parse(templatefile)
        # Assume that the template is actually an Interchange file with empty
        # elements.
        object_template = root.find(config.record_tag)
        if object_template is None:
            # Ok, so maybe it really is a template
            object_template = root.find(f'./template/{config.record_tag}')
            if object_template is None:
                raise ValueError(f'Cannot find the {config.record_tag} element'
                                 f' from root or from ./template')
    return object_template


def get_template_from_csv(row: dict[str]):
    """
    The YAML configuration file defines tags and filenames for templates such as:
        book: 2022-10-17_books_template.xml
    See the doc for the complete template_***: syntax.
    The CSV file contains a column with values such as "book" indicating which
    template should be used to create an object.

    :param row: a row from the CSV file
    :return: the template as an ElementTree element
    :raises: ValueError if the key from the CSV file is not in the config.
    """
    key = row[config.template_title].lower()
    if key not in config.templates:
        msg = (f'Template key in CSV file: "{key}" is not in config.'
               f' row: {list(row.values())}')
        if _args.nostrict:
            trace(1, msg)
            return None
        raise ValueError(msg)
    templatefilepath = os.path.join(config.template_dir, config.templates[key])
    trace(3, 'template file: {}', templatefilepath)
    return get_object_from_file(templatefilepath)


def store(xpath: str, doc, template, accnum, text):
    """

    :param xpath: The xpath or xpath2 from the document
    :param doc: The full document
    :param template: The template xml to be populated
    :param accnum: The accession number from the CSV file
    :param text: The text from the CSV file to store
    :return: None
    """
    trace(2, 'serial: {}, xpath: {}, text: {}', accnum, xpath, text)
    elt = template.find(xpath)
    cmd = doc[Stmt.CMD]
    if elt is None:
        elt = new_subelt(doc, template, accnum, _args.verbose)
    if elt is None:
        trace(1, 'Cannot create new element for {}, column "{}", value: "{}", element: {}\n'
                 'Check parent_path statement.',
              accnum, doc[Stmt.TITLE], text, doc[Stmt.XPATH], color=Fore.RED)
        return
    if cmd == Cmd.CONSTANT:
        elt.text = text
        return
    if cmd == Cmd.ITEMS:
        create_items(doc, elt, template, text)
    else:
        elt.text = text
    if Stmt.DATE in doc:
        # Only britishdate supported now
        try:
            elt.text, _, _ = modesdatefrombritishdate(elt.text)
            # print(type(elt.text))
        except ValueError:
            elt.text = 'unknown'
    elif Stmt.PERSON_NAME in doc:
        elt.text = modes_person(elt.text)


def main():
    global nrows
    if not _args.noprolog:
        outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    global_object_template = None
    # The command-line argument --template overrides the YML config value.
    if _args.template:
        global_object_template = get_object_from_file(_args.template)
    elif config.template_file:
        global_object_template = get_object_from_file(config.template_file)

    nrows = 0
    # PyCharm whines if we don't initialize variables
    accnumgen = next_accnum(_args.acc_num)
    ifcolumneq_doc = ifcolumneq_title = ifcolumneq_value = None
    for doc in config.ctrl_docs:
        if doc[Stmt.CMD] == Cmd.IFCOLUMNEQ:
            ifcolumneq_doc = doc
    if ifcolumneq_doc:
        ifcolumneq_title = ifcolumneq_doc[Stmt.TITLE]
        ifcolumneq_value = ifcolumneq_doc[Stmt.VALUE]
    for row in row_dict_reader(_args.incsvfile, _args.verbose,
                               _args.skiprows):
        if ifcolumneq_doc:
            if row[ifcolumneq_title] != ifcolumneq_value:
                trace(2, 'skipping {} row: {}',
                      row[ifcolumneq_title], row[config.serial])
                continue
        emit = True
        if global_object_template is not None:
            template = copy.deepcopy(global_object_template)
        else:
            template = get_template_from_csv(row)
        if template is None:  # template not found but nostrict is True
            continue
        elt = template.find(config.record_id_xpath)
        if _args.acc_num:
            accnum = next(accnumgen)
            trace(2, 'Serial generated: {}', accnum)
        else:
            trace(3, '{}', row)
            accnum = row[config.serial]
            if not accnum:
                trace(1, '\n*** Serial number empty, row skipped: {}', ','.
                      join(row.values()), color=Fore.RED)
                continue
            if config.add_mda_code and accnum[0].isnumeric():
                accnum = _args.mdacode + '.' + accnum
        accnum = clean_accnum(accnum)
        elt.text = accnum
        for doc in config.col_docs:
            cmd = doc[Stmt.CMD]
            # print(f'cmd: {doc[Stmt.CMD]}')
            title = doc[Stmt.TITLE]
            column_title = doc[Stmt.COLUMN_TITLE]
            if cmd == Cmd.REPRODUCTION:
                text = accnum + '.jpg'
            elif cmd == Cmd.CONSTANT:
                text = doc[Stmt.VALUE]
            else:
                text = row[column_title]
            trace(4, 'column="{}", text="{}"', column_title, text)
            if not process_if_other_column(row, doc, accnum):
                continue
            if cmd != Cmd.CONSTANT and not text:
                trace(3, '{}: cell empty {}', accnum, title)
                if Stmt.REQUIRED in doc:
                    print(f'*** Required column “{title}” is missing from'
                          f' {accnum}. Object excluded.')
                    emit = False
                continue
            if text == '{{clear}}':
                text = ''
            elif text == '{{today}}':
                text = _args.date
            xpath = doc[Stmt.XPATH]
            store(xpath, doc, template, accnum, text)
            if Stmt.XPATH2 in doc:
                store(doc[Stmt.XPATH2], doc, template, accnum, text)
        if emit:
            nrows += 1
            outfile.write(ET.tostring(template))
    if not _args.noprolog:
        outfile.write(b'</Interchange>')
        trace(2, 'Writing </Interchange>')


def getparser():
    parser = argparse.ArgumentParser(description=sphinxify('''
        Read a CSV file containing two or more columns. The first column
        is the accession number and the following columns are the fields
        defined by the XPATH statement(s) in the config file. The first row in the
        CSV file is a heading row. The column titles in the CSV file must match
        the document titles in the config file; case is significant. Columns
        are referred to by name so columns not named in the config file are
        ignored. After the first column the columns may be in any order.
        
        Create an XML file with data from the CSV file based on a template of
        the XML structure.
                ''', calledfromsphinx))
    parser.add_argument('--acc_num', help='''
        This is the first accession number in a series to assign to rows
        in the input CSV file. If specified, the column in the CSV file
        containing an accession number, if one exists, is ignored. For example,
        if the parameter is "LDHRM.2021.2", the numbers assigned will be
        "LDHRM.2021.2", "LDHRM.2021.3", etc. This value will be stored in the
        ObjectIdentity/Number element.''')
    parser.add_argument('-c', '--cfgfile', required=True,
                        type=argparse.FileType(), help=sphinxify('''
        The YAML file describing the column path(s) to update.
        The config file may contain only ``column``, ``constant``, or
        ``items`` column-related commands or template-related commands.
    ''', calledfromsphinx))
    parser.add_argument('-d', '--date', help='''
        If a column in the CSV file contains '{{today}}', use this value for
        the field text. The default is today’s date.
        ''')
    parser.add_argument('-i', '--incsvfile', required=True, help=sphinxify('''
        The file containing data to be inserted into the XML template.
        The file must have a heading, but see option --skiprows.
        The heading of the column containing the serial number must be
        ``Serial`` or an alternative set by --serial parameter. Subsequent
        columns must match the corresponding title in the configuration file.
        The file must have a (case-insensitive) suffix of ``.csv`` or ``.xlsx``
        containing CSV format or Excel format data,
        respectively.''', calledfromsphinx))
    parser.add_argument('-m', '--mdacode', default=DEFAULT_MDA_CODE, help=f'''
        Specify the MDA code, used in normalizing the accession number.''' +
                        if_not_sphinx(f''' The default is "{DEFAULT_MDA_CODE}".
                        ''', calledfromsphinx))
    parser.add_argument('-n', '--nostrict', action='store_true',
                        help=sphinxify('''
        Allow the absence of a template file with a key that matches the
        corresponding value in the column of the CSV file specified by
        --template. The row will be skipped. The default behavior is to
        raise a ValueError exception.''', calledfromsphinx))
    parser.add_argument('-o', '--outfile', required=True, help='''
        The output XML file.''')
    parser.add_argument('-p', '--noprolog', action='store_true', help='''
        Inhibit the insertion of an XML prolog at the front of the file and an
        <Interchange> element as the root. This results in an invalid XML file
        but is useful if the output is to be manually edited.''')
    parser.add_argument('--serial', default='Serial',
                        deprecated=True, help=sphinxify('''
        The column containing the serial number (the first column) must have a
        heading with this value. This is ignored if the --acc_num parameter is
        specified. This argument is deprecated. Use the
        ``serial:`` global configuration statement.
        ''' + if_not_sphinx('''
        The default value is "Serial".''', calledfromsphinx),
                                       calledfromsphinx))
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('--skiprows', type=int, default=0, help='''
        Skip rows at the beginning of the CSV file.''')
    parser.add_argument('-t', '--template', help=sphinxify('''
        The XML file that is the template for creating the output XML.
        Specify this or template-related statements in the configuration.
        ''', calledfromsphinx))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if args.date:
        args.date, _, _ = modesdatefrombritishdate(args.date)
    else:
        args.date = modesdate(date.today())
    return args


def check_cfg(c):
    """
    Allow a restricted number of commands.
    :param c: The Config instance
    :return: Nonzero if the config fails.
    """
    errs = 0
    for doc in c.col_docs:
        if doc[Stmt.CMD] not in (Cmd.COLUMN, Cmd.CONSTANT, Cmd.ITEMS, Cmd.REPRODUCTION):
            trace(0, 'Column-oriented command "{}" not allowed,'
                     ' exiting.',
                  doc[Stmt.CMD], color=Fore.RED)
            errs += 1
    for doc in c.ctrl_docs:
        if doc[Stmt.CMD] == Cmd.IFCOLUMNEQ:
            continue
        trace(0, 'Control command "{}" not allowed, exiting.',
              doc[Stmt.CMD], color=Fore.RED)
        errs += 1
    if c.template_file and c.templates:
        trace(0, 'Do not specify the template_file statement with'
              ' other template-related statements.', color=Fore.RED)
        errs += 1
    return errs


calledfromsphinx = True


if __name__ == '__main__':
    global nrows
    assert sys.version_info >= (3, 9)
    calledfromsphinx = False
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}', _args.incsvfile)
    trace(1, 'Creating file: {}', _args.outfile)
    config: Config = Config(_args.cfgfile, dump=_args.verbose > 1,
                            allow_required=True)
    if errors := check_cfg(config):
        trace(1, '{} error(s) found. Aborting.', errors)
        sys.exit(1)
    trace(1, 'Begin csv2xml.', color=Fore.GREEN)
    if not config.serial:
        config.serial = _args.serial
    main()
    trace(1, 'End csv2xml. {} object{} written.', nrows,
          '' if nrows == 1 else 's', color=Fore.GREEN)
