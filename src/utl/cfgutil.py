import codecs
from colorama import Fore, Style
import csv
import os
import re
import sys

# import yaml
from ruamel.yaml import YAML
import ruamel.yaml.constructor

# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.normalize import normalize_id
yaml = YAML(typ='safe')   # default, if not specfied, is 'rt' (round-trip)

# The difference between the 'attrib' command and the attribute statement:
# The 'attrib' command is just like the column command except that the value of
# the attribute given in the attribute statement is extracted.
# The 'attribute' statement is also used in the case of the 'ifattrib' command
# to name the attribute to test against the 'value' statement.
# Note that the 'ifattrib' command is redundant: You can use the 'if'
# statement with an appropriate xpath like .[@elementtype="ephemera"].


def trace(level, verbose, template, *args, color=None):
    if verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


class Cmd:
    """
    Define the configuration commands. This is the value of the "cmd:" statement.

    IMPORTANT: Variables that are not literal commands must be prefaced with
    the "_" character to separate them from variables that are literal commands.
    Details are to be found in the Sphinx documentation for this project.
    """
    ATTRIB = 'attrib'
    COLUMN = 'column'
    CONSTANT = 'constant'
    MULTIPLE = 'multiple'
    COUNT = 'count'
    DELETE = 'delete'
    DELETE_ALL = 'delete_all'
    GLOBAL = 'global'
    KEYWORD = 'keyword'
    ITEMS = 'items'
    # "IF" commands follow:
    IF = 'if'  # if text is present
    IFELT = 'ifelt'  # if the element is present
    IFNOT = 'ifnot'  # if text is not present
    IFATTRIB = 'ifattrib'  # requires attribute statement
    IFATTRIBEQ = 'ifattribeq'  # requires attribute statement
    IFATTRIBNOTEQ = 'ifattribnoteq'  # requires attribute statement
    IFCONTAINS = 'ifcontains'
    IFEQ = 'ifeq'  # if the elt text equals the value statement
    IFNOTEQ = 'ifnoteq'  # if the elt text does not equal the value statement
    # Commands that do not produce a column in the output CSV file
    _CONTROL_CMDS = (IF, IFNOT, IFEQ, IFNOTEQ, IFATTRIB, GLOBAL,
                     IFCONTAINS, IFATTRIBEQ, IFATTRIBNOTEQ, IFELT)
    _NEEDVALUE_CMDS = (KEYWORD, IFEQ, IFNOTEQ, IFATTRIBEQ, IFATTRIBNOTEQ,
                       IFCONTAINS, CONSTANT)
    _NEEDXPATH_CMDS = (ATTRIB, COLUMN, CONSTANT, COUNT, ITEMS, IF, IFNOT, IFELT, IFEQ,
                       IFNOTEQ, IFCONTAINS, IFATTRIB, IFATTRIBEQ,
                       IFATTRIBNOTEQ, KEYWORD, MULTIPLE)

    @staticmethod
    def get_needxpath_cmds():
        return Cmd._NEEDXPATH_CMDS

    @staticmethod
    def get_needvalue_cmds():
        return Cmd._NEEDVALUE_CMDS

    @staticmethod
    def get_control_cmds():
        return Cmd._CONTROL_CMDS

    @staticmethod
    def validate_yaml_cmd(cmd):
        validlist = [getattr(Cmd, c) for c in dir(Cmd)
                     if isinstance(getattr(Cmd, c), str) and not c.startswith('_')
                     ]
        # print('validlist', validlist)
        valid = cmd in validlist
        if not valid:
            print(f'{cmd} is not a valid command.')
        return valid


class Stmt:
    """
    Define the configuration statements.

    IMPORTANT: Variables that are not literal statements must be prefaced with
    the "_" character to separate them from variables that are literal statements.
    This is because we do a dir(Stmt) to get a list of valid statements,
    excluding those beginning with '_'.
    """
    ADD_MDA_CODE = 'add_mda_code'
    ATTRIBUTE = 'attribute'
    ATTRIBUTE_VALUE = 'attribute_value'
    CASE_SENSITIVE = 'case_sensitive'
    CHILD = 'child'
    CHILD_VALUE = 'child_value'
    CMD = 'cmd'
    DATE = 'date'
    DELIMITER = 'delimiter'
    ELEMENT = 'element'
    INSERT_AFTER = 'insert_after'
    MULTIPLE_DELIMITER = 'multiple_delimiter'
    NORMALIZE = 'normalize'
    PARENT_PATH = 'parent_path'
    PERSON_NAME = 'person_name'
    RECORD_TAG = 'record_tag'
    RECORD_ID_XPATH = 'record_id_xpath'
    REQUIRED = 'required'
    SKIP_NUMBER = 'skip_number'
    SORT_NUMERIC = 'sort_numeric'
    TEMPLATE_DIR = 'template_dir'
    TEMPLATE_FILE = 'template_file'
    TEMPLATE_TITLE = 'template_title'
    TEMPLATES = 'templates'
    TITLE = 'title'
    VALUE = 'value'
    WIDTH = 'width'
    XPATH = 'xpath'
    XPATH2 = 'xpath2'
    _DEFAULT_RECORD_TAG = 'Object'
    _DEFAULT_RECORD_ID_XPATH = './ObjectIdentity/Number'

    @staticmethod
    def get_default_record_id_xpath():
        return Stmt._DEFAULT_RECORD_ID_XPATH

    @staticmethod
    def get_default_record_tag():
        return Stmt._DEFAULT_RECORD_TAG

    @staticmethod
    def validate_yaml_stmts(document):
        validlist = [getattr(Stmt, stmt) for stmt in dir(Stmt)
                     if not stmt.startswith('_')]
        valid = True
        for stmt in document:
            if stmt not in validlist:
                print(f'"{stmt}" is not a valid statement.')
                valid = False
        return valid


class Config:
    __instance = None

    @staticmethod
    def get_config():
        if Config.__instance is None:
            raise Exception('Config instance not created.')
        return Config.__instance

    @staticmethod
    def reset_config():
        """
        This is necessary when called by test_xml2csv
        :return: None
        """
        Config.__instance = None

    def __init__(self, yamlcfgfile=None, dump: bool = False,
                 allow_required: bool = False, logfile=sys.stdout):
        """

        :param yamlcfgfile: If None then only the default global values will
                            be initialized.
        :param dump: If True, print the YAML documents
        :param allow_required: If True, allow the REQUIRED statement under the
                               COLUMN command. This only makes sense for
                               csv2xml.py.
        :returns: the Config instance or None if the YAML file is not given
        """
        def set_globals():
            for stmt in document:
                if stmt == Stmt.CMD:
                    continue
                elif stmt == Stmt.SKIP_NUMBER:
                    self.skip_number = True
                elif stmt == Stmt.SORT_NUMERIC:
                    self.sort_numeric = True
                elif stmt == Stmt.RECORD_ID_XPATH:
                    self.record_id_xpath = document[stmt]
                elif stmt == Stmt.RECORD_TAG:
                    self.record_tag = document[stmt]
                elif stmt == Stmt.DELIMITER:
                    self.delimiter = document[stmt]
                elif stmt == Stmt.MULTIPLE_DELIMITER:
                    self.multiple_delimiter = document[stmt]
                elif stmt == Stmt.ADD_MDA_CODE:
                    self.add_mda_code = True
                elif stmt == Stmt.TEMPLATE_DIR:
                    self.template_dir = document[stmt]
                elif stmt == Stmt.TEMPLATE_FILE:
                    self.template_file = document[stmt]
                elif stmt == Stmt.TEMPLATE_TITLE:
                    self.template_title = document[stmt]
                elif stmt == Stmt.TEMPLATES:
                    templates = yaml.load(document[stmt])
                    self.templates = {key.lower(): value for key, value in
                                      templates.items()}
                else:
                    print(f'Unknown statement, ignored: {stmt}.')
            if self.templates or self.template_title or self.template_dir:
                if not (self.templates and self.template_title and
                        self.template_dir):
                    raise ValueError('All of the global statements '
                                     'templates, template_title, and '
                                     'template_dir must be specified if one '
                                     'is.')
        if Config.__instance is not None:
            raise ValueError("This class is a singleton!")
        Config.__instance = self
        self.logfile = logfile
        self.col_docs = []  # documents that generate columns
        self.ctrl_docs = []  # control documents
        self.skip_number = False
        self.sort_numeric = False
        self.add_mda_code = False
        self.templates = None
        self.template_title = None
        self.template_dir = None
        self.template_file = None
        self.record_tag = Stmt.get_default_record_tag()
        self.record_id_xpath = Stmt.get_default_record_id_xpath()
        self.delimiter = ','
        self.multiple_delimiter = '|'
        cfglist = _read_yaml_cfg(yamlcfgfile, dump=dump, logfile=logfile)
        valid = validate_yaml_cfg(cfglist, allow_required)
        if not valid:
            sys.tracebacklimit = 0
            raise ValueError(Fore.RED + 'Config failed validation.' + Style.RESET_ALL)
        for document in cfglist:
            cmd = document[Stmt.CMD]
            if cmd == Cmd.GLOBAL:
                set_globals()
            elif cmd in Cmd.get_control_cmds():
                self.ctrl_docs.append(document)
            else:  # not control command
                self.col_docs.append(document)
        self.norm = []  # True if this column needs to normalized/unnormalized
        # Do this as a separate step because we didn't know whether we need
        # to include the serial number until all the documents were read.
        if not self.skip_number:
            self.norm.append(True)  # for the Serial number
        for doc in self.col_docs:
            self.norm.append(Stmt.NORMALIZE in doc)
            if Stmt.MULTIPLE_DELIMITER not in doc:
                doc[Stmt.MULTIPLE_DELIMITER] = self.multiple_delimiter
        self.lennorm = len(self.norm)
        if len(self.ctrl_docs):
            print("Config contains filtering commands.")

    def select(self, elem, include_list=None, exclude=False):
        return select(self, elem, include_list, exclude)


def new_subelt(doc, obj, idnum, verbos=1):
    """

    :param doc: The YAML document for this column (or constant)
    :param obj: The Object element
    :param idnum: Used for debugging
    :param verbos:
    :return:
    """
    if Stmt.PARENT_PATH not in doc:
        return None
    newelt = None
    title = doc[Stmt.TITLE]
    element = doc[Stmt.ELEMENT]
    insert_after = doc.get(Stmt.INSERT_AFTER)
    trace(3, verbos, 'new_subelt: {}, element={}, insert_after={} ',
          idnum, element, insert_after)
    parent = obj.find(doc[Stmt.PARENT_PATH])
    if parent is None:
        trace(1, verbos, 'Cannot find parent of {}, column {}',
              doc[Stmt.XPATH], title, color=Fore.YELLOW)
    elif ' ' in element:
        trace(1, verbos, 'Cannot create element with embedded spaces: {}',
              element, color=Fore.YELLOW)
    elif insert_after is None:
        newelt = ET.SubElement(parent, element)
    elif insert_after == '':
        newelt = ET.Element(element)
        parent.insert(0, newelt)
    else:
        elts = list(parent)
        insert_ix = None
        # Insert after the last element named in the insert_after statement.
        for n, e in enumerate(elts):
            if e.tag == insert_after:
                insert_ix = n + 1
        if insert_ix is None:
            trace(1, verbos, '{}: Cannot find insert_after element "{}", '
                  'inserting at end.', idnum, insert_after, color=Fore.YELLOW)
            newelt = ET.SubElement(parent, element)
        else:
            newelt = ET.Element(element)
            parent.insert(insert_ix, newelt)
    if newelt is not None:
        if Stmt.CHILD in doc:
            childelt = ET.SubElement(newelt, doc[Stmt.CHILD])
            if Stmt.CHILD_VALUE in doc:
                childelt.text = doc.get(Stmt.CHILD_VALUE, '')
        if Stmt.ATTRIBUTE in doc:
            value = doc[Stmt.ATTRIBUTE_VALUE] if Stmt.ATTRIBUTE_VALUE in doc else ''
            newelt.set(doc[Stmt.ATTRIBUTE], value)
    return newelt


def select(cfg: Config, elem, includes=None, exclude=False):
    """
    :param cfg: the Config instance
    :param elem: the Object element
    :param includes: A set or dict of id numbers of objects to be included
                     in the output CSV file. The list must be all uppercase.
    :param exclude: Treat the include list as an exclude list.
    :return: selected is true if the Object element should be written out
    """
    # print('select')
    selected = True
    idelem = elem.find(cfg.record_id_xpath)
    idnum = normalize_id(idelem.text) if idelem is not None else None
    # print(f'{idnum=}')
    if idnum and exclude and includes:
        if idnum in includes:
            return False
    elif includes is not None:
        if not idnum or idnum not in includes:
            # print('select return false')
            return False
    for document in cfg.ctrl_docs:
        command = document[Stmt.CMD]
        if command == Cmd.GLOBAL:
            continue
        eltstr = document.get(Stmt.XPATH)
        if eltstr:
            element = elem.find(eltstr)
        else:
            element = None
        # print(f'{element=}')
        if element is None:
            if Stmt.REQUIRED in document:
                print(f'*** Required element {eltstr} is missing from'
                      f' {idnum}. Object excluded.', file=cfg.logfile)
            selected = False
            break
        elif command == Cmd.IFELT:
            continue  # if the element exists
        if command in (Cmd.ATTRIB, Cmd.IFATTRIB, Cmd.IFATTRIBEQ, Cmd.IFATTRIBNOTEQ):
            attribute = document[Stmt.ATTRIBUTE]
            text = element.get(attribute).strip()
        elif element is None or element.text is None:
            text = ''
        else:
            # noinspection PyUnresolvedReferences
            text = element.text.strip()
        # print(f'{text=}')
        if text:
            if command == Cmd.IFNOT:
                selected = False
                break
        else:
            if Stmt.REQUIRED in document:
                print(f'*** Required text in {eltstr} is missing from'
                      f' {idnum}. Object excluded.', file=cfg.logfile)
            if command in (Cmd.IF, Cmd.IFATTRIB, Cmd.IFCONTAINS,
                           Cmd.IFEQ, Cmd.IFATTRIBEQ):
                selected = False
                break
        if command in (Cmd.IFEQ, Cmd.IFNOTEQ, Cmd.IFCONTAINS,
                       Cmd.IFATTRIBEQ, Cmd.IFATTRIBNOTEQ):
            value = document[Stmt.VALUE]
            textvalue = text
            if Stmt.CASE_SENSITIVE not in document:
                value = value.lower()
                textvalue = textvalue.lower()
            if command == Cmd.IFCONTAINS and value not in textvalue:
                selected = False
                break
            elif (command in (Cmd.IFEQ, Cmd.IFATTRIBEQ)
                  and value != textvalue):
                selected = False
                break
            elif (command in (Cmd.IFNOTEQ, Cmd.IFATTRIBNOTEQ)
                  and value == textvalue):
                selected = False
                break
            continue
    # print(f'{selected=}')
    return selected


def dump_document(document, logfile=sys.stdout):
    print('Document:', file=logfile)
    for stmt in document:
        print(f'     {stmt}: {document[stmt]}', file=logfile)
    print('     ---', file=logfile)


def validate_yaml_cfg(cfglist, allow_required=False, logfile=sys.stdout):
    valid = True
    for document in cfglist:
        # Do not change this to valid_doc = Stmt.val.... to allow for more
        # tests before this one.
        valid_doc = True
        if not Stmt.validate_yaml_stmts(document):
            valid_doc = False
        if Stmt.CMD not in document:
            print('ERROR: cmd statement is missing.', file=logfile)
            valid = False
            dump_document(document, logfile=logfile)
            break
        command = document[Stmt.CMD]
        if not Cmd.validate_yaml_cmd(command):
            valid_doc = False
        # These commands are mutually exclusive as they change the data in
        # incompatible ways.
        only_one = (Stmt.PERSON_NAME, Stmt.DATE, Stmt.NORMALIZE)
        if [True for s in only_one if s in document].count(True) > 1:
            print(f'ERROR: Only one of {", ".join(only_one)} allowed.')
            valid_doc = False
        if command in Cmd.get_needxpath_cmds() and Stmt.XPATH not in document:
            print(f'{Fore.RED}ERROR: XPATH statement missing, cmd: '
                  f'{command}{Style.RESET_ALL}', file=logfile)
            valid_doc = False
        if command in Cmd.get_needvalue_cmds() and Stmt.VALUE not in document:
            print(f'ERROR: value is required for {command} command.', file=logfile)
            valid_doc = False
        if command in (Cmd.ATTRIB, Cmd.IFATTRIB, Cmd.IFATTRIBEQ):
            if Stmt.ATTRIBUTE not in document:
                print(f'ERROR: attribute is required for {command} command.', file=logfile)
                valid_doc = False
        if command not in Cmd.get_control_cmds():
            # for csv2xml.py allow required on a column command
            if Stmt.REQUIRED in document:
                if not (command == Cmd.COLUMN and allow_required):
                    print(f'ERROR: "required" not allowed for {command} '
                          f'command. Use an "if" command.', file=logfile)
                    valid_doc = False
        if not valid_doc:
            valid = False
            dump_document(document, logfile=logfile)

    return valid


def _read_yaml_cfg(cfgf, dump: bool = False, logfile=sys.stdout):
    """
    Called by the Config constructor. Return the YAML documents with minor
    additions.

    :param cfgf: The YAML file specifying the configuration. Might be None
                 for an empty document, like trailing "---". An empty Config
                 may be used to get the default values.
    :param dump: if True, dump YAML documents as processed.
    :return: A list of dicts, each of which is a YAML document. If the config
             file was not specified on the command line, then return an empty
             list.
    """
    if cfgf is None:
        return []
    try:
        cfg = [c for c in yaml.load_all(cfgf) if c is not None]
    except ruamel.yaml.constructor.DuplicateKeyError as e:
        print(e.args)
        sys.exit()
    titles = set()
    for document in cfg:
        for key in document:
            if document[key] is None:
                document[key] = ''
            document[key] = str(document[key])
        if dump:
            dump_document(document, logfile=logfile)
        if Stmt.CMD not in document:
            if not dump:
                dump_document(document, logfile=logfile)
            print('"cmd" statement missing from document.')
            sys.exit()
        cmd = document[Stmt.CMD]
        if cmd in Cmd.get_control_cmds():
            continue
        # Specify the column title. If the title isn't specified in the doc,
        # construct the title from the trailing element name from the xpath
        # statement. The validate_yaml_cfg function checks that the xpath
        # statement is there if needed.
        # print('readyaml')
        if Stmt.TITLE not in document:
            if Stmt.XPATH not in document:
                continue  # error will be caught later
            target = document.get(Stmt.XPATH)
            # print('target', target)
            attribute = document.get(Stmt.ATTRIBUTE)
            h = target.split('/')[-1]  # trailing element name
            target = h.split('[')[0]  # strip trailing [@xyz='def']
            if attribute:
                target += '@' + attribute
            elif cmd == Cmd.COUNT:
                target = f'{target}(n)'
            document[Stmt.TITLE] = target
        if Stmt.PARENT_PATH in document and Stmt.ELEMENT not in document:
            document[Stmt.ELEMENT] = document[Stmt.TITLE]

        if document[Stmt.TITLE] in titles:
            raise ValueError(f'Duplicate title "{document[Stmt.TITLE]}"')
        titles.add(document[Stmt.TITLE])
    return cfg


def yaml_fieldnames(config):
    """
    :param config: The Config
    :return: a list of column headings extracted from the column-generating
    statements.
    """
    hdgs = []
    if not config.skip_number:
        hdgs.append('Serial')  # hardcoded first entry
    for doc in config.col_docs:
        hdgs.append(doc[Stmt.TITLE])
    return hdgs


def _splitid(idstr: str, m: re.Match) -> (str, int, int, int):
    """
    Subroutine to expand_one_idnum.
    Do the common processing for the "-" and "&" cases.

    Consider the case of JB121-24.

    :return: prefix = "JB1"
             variablepart: int = 21
             intsecondidnum: int = 24
             len(variablepart) = 2
    """
    prefix = m[1]  # will be updated later if 2nd # is shorter than 1st #
    lenprefix = len(prefix)
    firstidnum = m[2]
    intsecondidnum = int(m[3])  # the numbers after the '-' or '&'
    # lenfirstid will change if the second # is shorter than the first
    lenfirstid = len(firstidnum)
    lenlastid = len(m[3])
    lenfixedpart = max(lenfirstid - lenlastid, 0)
    # In a case like SH21-4, the fixed part will be the leading part of the
    # number, in this case "2".
    fixedpart = idstr[lenprefix:lenprefix + lenfixedpart]
    variablepart = idstr[lenprefix + lenfixedpart:lenprefix + lenfirstid]
    prefix += fixedpart
    intvariablepart = int(variablepart)
    if intvariablepart >= intsecondidnum:
        raise ValueError(f'{idstr} first number must be less than last number')
    return prefix, intvariablepart, intsecondidnum, len(variablepart)


def _expand_one_idnum(idstr: str) -> list[str]:
    """
    :param idstr: An accession number or a range of numbers. If it is a range,
    indicated by a hyphen or ampersand anywhere in the string, the format of
    the number is:
        idstr ::= idnum | rangestr | liststr
        idnum ::= string without '-/&'
        rangestr ::= prefix-suffix | prefix/suffix
        liststr ::=  prefix&suffix | liststr&suffix
        prefix ::= text<n digits>
        suffix ::= <n digits>
        The suffix is a string of digits terminating the idstr.
        The prefix consists of any text (possibly including trailing digits).
        An idnum is a single complete accession number. It might be passed to
        expand_one_idnum if expand_idnum is called with a comma-delimited list.
        Note: white space is removed from the idnum before parsing.

    :return: A list containing zero or more idnums. If idnum is just a single
    number, then it will be returned inside a list. If there is an error,
    an empty list will be returned. If a range is specified, then multiple
    idnums will be returned in the list. If a second suffix rather than a
    range is given, specified by an "&", then two accession numbers are returned.

    Examples:
        JB021-024 or JB021-24. These produce identical results:
            ['JB021', 'JB022', 'JB023', 'JB024']
        JB021&026&033 returns:
            ['JB021', 'JB026', 'JB033']
    """

    jlist = []
    idstr = ''.join(idstr.split())  # remove all whitespace
    if '-' in idstr or '/' in idstr:  # if ID is actually a range like JB021-23
        if m := re.match(r'(.+?)(\d+)[-/](\d+)$', idstr):
            prefix, num1, num2, lenvariablepart = _splitid(idstr, m)
            try:
                for suffix in range(num1, num2 + 1):
                    newidnum = f'{prefix}{suffix:0{lenvariablepart}}'
                    jlist.append(newidnum)
            except ValueError:
                print(f'Bad accession number, contains "-" but not well'
                      f' formed: {m.groups()}')
        else:
            print('Bad accession number, failed pattern match:', idstr)
    elif '&' in idstr:
        parts = idstr.split('&')
        head = parts[0]
        jlist.append(head)
        for tail in parts[1:]:
            # Really don't have to do this. Better to extract prefix and num1
            # from the head once and tail becomes num2. But this is good enough.
            partstr = f'{head}&{tail}'
            if m := re.match(r'(.+?)(\d+)&(\d+)$', partstr):
                prefix, num1, num2, lenvariablepart = _splitid(idstr, m)
                newidnum = f'{prefix}{num2:0{lenvariablepart}}'
                jlist.append(newidnum)
            else:
                print('Bad accession number, failed pattern match:', idstr)

    else:
        jlist.append(idstr)
    return jlist


def expand_idnum(idnumstr: str) -> list[str]:
    """
    Expand an idnumstr to a list of idnums.
    :param idnumstr: (See expand_one_idnum for the definition of idstr)
        idnumstr ::= idstr | idnumstr,idstr
    :return: list of idnums
    """
    idstrlist = idnumstr.split(',')
    rtnlist = []
    for idstr in idstrlist:
        rtnlist += _expand_one_idnum(idstr)
    return rtnlist


def read_include_dict(includes_file, include_column, include_skip, verbos=1,
                      logfile=sys.stdout, allow_blanks=False, mdacode=''):
    """
    Read the optional CSV file from the --include argument. Build a dict
    of normalized accession IDs for use by cfgutil.select. The value
    of the dict is the row from the CSV file. Function expand_num is called
    so one row in the CSV file may result in multiple entries in the dict.
    :return: a dict or None if --include was not specified
    """

    if not includes_file:
        return None
    if os.path.splitext(includes_file)[1].lower() != '.csv':
        raise ValueError('--include file must be a CSV file.')
    includedict: dict = dict()
    includereader = csv.reader(codecs.open(includes_file, 'r', 'utf-8-sig'))
    for n in range(include_skip):  # default in xml2csv = 0
        skipped = next(includereader)  # skip header
        if verbos >= 1:
            print(f'Skipping row in "include" file: {skipped}', file=logfile)
    for row in includereader:
        if not row:
            continue
        idnum = row[include_column].upper()  # cfgutil.select needs uppercase
        if not idnum:
            if allow_blanks:
                if verbos >= 1 and ''.join(row):
                    print(f'Skipping row with blank ID: {row}',
                          file=logfile)
                continue  # skip blank accession numbers
            else:
                raise ValueError('Blank accession number in include file;'
                                 ' --allow_blank not selected.')
        # idnumlist: list[str] = expand_idnum(idnum)
        if mdacode:
            idnum = mdacode + '.' + idnum
        idnumlist: list[str] = [normalize_id(i) for i in expand_idnum(idnum)]
        if verbos >= 1:
            for num in idnumlist:
                if num in includedict:
                    print(f'Warning: Duplicate id number in include '
                          f'file, {num}, ignored.', file=logfile)
        for idnum in idnumlist:
            includedict[idnum] = row
    return includedict
