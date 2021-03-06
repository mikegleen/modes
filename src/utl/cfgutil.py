import csv
import re
import sys

import yaml

# The difference between the 'attrib' command and the attribute statement:
# The 'attrib' command is just like the column command except that the attribute
# value as given in the attribute statement is extracted.
# The 'attribute' statement is also used in the case of the 'ifattrib' command
# to name the attribute to test against the 'value' statement.


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
    GLOBAL = 'global'
    KEYWORD = 'keyword'
    IF = 'if'  # if text is present
    IFATTRIB = 'ifattrib'  # requires attribute statement
    IFATTRIBEQ = 'ifattribeq'  # requires attribute statement
    IFATTRIBNOTEQ = 'ifattribnoteq'  # requires attribute statement
    IFCONTAINS = 'ifcontains'
    IFEQ = 'ifeq'  # if the elt text equals the value statement
    IFNOTEQ = 'ifnoteq'  # if the elt text does not equal the value statement
    IFSERIAL = 'ifserial'
    # Commands that do not produce a column in the output CSV file
    _CONTROL_CMDS = (IF, IFEQ, IFNOTEQ, IFATTRIB, IFSERIAL, GLOBAL, IFCONTAINS,
                     IFATTRIBEQ, IFATTRIBNOTEQ)
    _NEEDVALUE_CMDS = (KEYWORD, IFNOTEQ, IFATTRIBEQ, IFATTRIBNOTEQ, IFSERIAL,
                       IFCONTAINS, CONSTANT)
    _NEEDXPATH_CMDS = (ATTRIB, COLUMN, KEYWORD, IF, COUNT, IFEQ, IFNOTEQ,
                       IFCONTAINS, IFATTRIB, IFATTRIBEQ, IFATTRIBNOTEQ,
                       CONSTANT)

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
    CMD = 'cmd'
    XPATH = 'xpath'
    PARENT_PATH = 'parent_path'
    ATTRIBUTE = 'attribute'
    DATE = 'date'
    TITLE = 'title'
    VALUE = 'value'
    CASESENSITIVE = 'casesensitive'
    MULTIPLE_DELIMITER = 'multiple_delimiter'
    NORMALIZE = 'normalize'
    REQUIRED = 'required'
    WIDTH = 'width'
    SKIP_NUMBER = 'skip_number'
    RECORD_TAG = 'record_tag'
    RECORD_ID_XPATH = 'record_id_xpath'
    DELIMITER = 'delimiter'
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

    def __init__(self, yamlcfgfile, title: bool = False, dump: bool = False,
                 allow_required: bool = False):
        """

        :param yamlcfgfile:
        :param title: If no title statement exists, create one from the
                      XPATH statement.
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
                elif stmt == Stmt.RECORD_ID_XPATH:
                    self.record_id_xpath = document[stmt]
                elif stmt == Stmt.RECORD_TAG:
                    self.record_tag = document[stmt]
                elif stmt == Stmt.DELIMITER:
                    self.delimiter = document[stmt]
                elif stmt == Stmt.MULTIPLE_DELIMITER:
                    self.multiple_delimiter = document[stmt]
                else:
                    print(f'Unknown statement, ignored: {stmt}.')
        if Config.__instance is not None:
            raise ValueError("This class is a singleton!")
        Config.__instance = self
        self.col_docs = []  # documents that generate columns
        self.ctrl_docs = []  # control documents
        self.skip_number = False
        self.record_tag = Stmt.get_default_record_tag()
        self.record_id_xpath = Stmt.get_default_record_id_xpath()
        self.delimiter = ','
        self.multiple_delimiter = '|'
        cfglist = _read_yaml_cfg(yamlcfgfile, title=title, dump=dump)
        valid = validate_yaml_cfg(cfglist, allow_required)
        if not valid:
            raise ValueError('Config failed validation.')
        for document in cfglist:
            cmd = document[Stmt.CMD]
            if cmd == Cmd.GLOBAL:
                set_globals()
            elif cmd in Cmd.get_control_cmds():
                self.ctrl_docs.append(document)
            else:  # not control command
                self.col_docs.append(document)
        self.norm = []  # True if this column needs to normalized/unnormalized
        # Do this as a separate step because we don't know whether we need
        # to include the serial number until all of the documents are read.
        if not self.skip_number:
            self.norm.append(True)  # for the Serial number
        for doc in self.col_docs:
            self.norm.append(Stmt.NORMALIZE in doc)
        self.lennorm = len(self.norm)

    def select(self, elem, include_list=None, exclude=False):
        return select(self, elem, include_list, exclude)


def select(cfg: Config, elem, include_list=None, exclude=False):
    """
    :param cfg: the Config instance
    :param elem: the Object element
    :param include_list: A list of id numbers of objects to be included
                         in the output CSV file. The list must be all
                         uppercase.
    :param exclude: Treat the include list as an exclude list.
    :return: selected is true if the Object element should be written out
    """

    selected = True
    idelem = elem.find(cfg.record_id_xpath)
    idnum = idelem.text if idelem is not None else None
    # print(f'{idnum=}')
    if idnum and exclude and include_list:
        if idnum.upper() in include_list:
            return False
    elif include_list is not None:
        if not idnum or idnum.upper() not in include_list:
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
        if element is None:
            if Stmt.REQUIRED in document:
                print(f'*** Required element {eltstr} is missing from'
                      f' {idnum}. Object excluded.')
            selected = False
            break
        if command in (Cmd.ATTRIB, Cmd.IFATTRIB, Cmd.IFATTRIBEQ,
                       Cmd.IFATTRIBNOTEQ):
            attribute = document[Stmt.ATTRIBUTE]
            text = element.get(attribute)
        elif element.text is None:
            text = ''
        else:
            # noinspection PyUnresolvedReferences
            text = element.text.strip()
        if not text:
            if Stmt.REQUIRED in document:
                print(f'*** Required text in {eltstr} is missing from'
                      f' {idnum}. Object excluded.')
            if command in (Cmd.IF, Cmd.IFATTRIB, Cmd.IFCONTAINS,
                           Cmd.IFEQ, Cmd.IFATTRIBEQ):
                selected = False
                break
        if command in (Cmd.IFEQ, Cmd.IFNOTEQ, Cmd.IFCONTAINS,
                       Cmd.IFATTRIBEQ, Cmd.IFATTRIBNOTEQ):
            value = document[Stmt.VALUE]
            textvalue = text
            if Stmt.CASESENSITIVE not in document:
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
    return selected


def dump_document(document):
    print('Document:')
    for stmt in document:
        print(f'     {stmt}: {document[stmt]}')
    print('     ---')


def validate_yaml_cfg(cfglist, allow_required=False):
    valid = True
    for document in cfglist:
        # Do not change this to valid_doc = Stmt.val.... to allow for more
        # tests before this one.
        valid_doc = True
        if not Stmt.validate_yaml_stmts(document):
            valid_doc = False
        if Stmt.CMD not in document:
            print('ERROR: cmd statement is missing.')
            valid = False
            dump_document(document)
            break
        command = document[Stmt.CMD]
        if not Cmd.validate_yaml_cmd(command):
            valid_doc = False
        if command in Cmd.get_needxpath_cmds() and Stmt.XPATH not in document:
            print(f'ERROR: XPATH statement missing, cmd: {command}')
            valid_doc = False
        if command in Cmd.get_needvalue_cmds() and Stmt.VALUE not in document:
            print(f'ERROR: value is required for {command} command.')
            valid_doc = False
        if command in (Cmd.ATTRIB, Cmd.IFATTRIB, Cmd.IFATTRIBEQ):
            if Stmt.ATTRIBUTE not in document:
                print(f'ERROR: attribute is required for {command} command.')
                valid_doc = False
        if command not in Cmd.get_control_cmds():
            # for csv2xml.py allow required on a column command
            if Stmt.REQUIRED in document:
                if not (command == Cmd.COLUMN and allow_required):
                    print(f'ERROR: "required" not allowed for {command} '
                          f'command. Use an "if" command.')
                    valid_doc = False
        if not valid_doc:
            valid = False
            dump_document(document)

    return valid


def _read_yaml_cfg(cfgf, title: bool = False, dump: bool = False):
    """
    Called by the Config constructor. Return the YAML documents with minor
    additions.

    :param cfgf: The YAML file specifying the configuration
    :param title: if True, guarantee that all columns have a title. This is
                    necessary if, e.g., we are creating an output CSV file
                    with a title row.
    :param dump: if True, dump YAML documents as processed.
    :return: A list of dicts, each of which is a YAML document
    """
    # Might be None for an empty document, like trailing "---"
    if cfgf is None:
        return []
    cfg = [c for c in yaml.safe_load_all(cfgf) if c is not None]
    for document in cfg:
        for key in document:
            document[key] = str(document[key])
        if dump:
            dump_document(document)
        if Stmt.CMD not in document:
            if not dump:
                dump_document(document)
            print('"cmd" statement missing from document.')
            sys.exit()
        cmd = document[Stmt.CMD]
        if cmd in Cmd.get_control_cmds():
            continue
        # Specify the column title. If the title isn't specified in the doc,
        # construct the title from the trailing element name from the xpath
        # statement. The validate_yaml_cfg function checks that the xpath
        # statement is there if needed.
        if title and Stmt.TITLE not in document:
            target = document.get(Stmt.XPATH)
            attribute = document.get(Stmt.ATTRIBUTE)
            h = target.split('/')[-1]  # trailing element name
            target = h.split('[')[0]  # strip trailing [@xyz='def']
            if attribute:
                target += '@' + attribute
            elif cmd == Cmd.COUNT:
                target = f'{target}(n)'
            document[Stmt.TITLE] = target
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


def expand_idnum(idstr: str) -> list[str]:
    """
    :param idstr: An accession number or a range of numbers. If it is a range,
    indicated by a hyphen anywhere in the string, the format of the number is:
        idstr ::= <prefix>-<suffix>
        prefix ::= <any text><n digits>
        suffix ::= <n digits>
        The prefix consists of any text followed by a string of digits of the
        same length as the suffix.
        The suffix is a string of digits.
    :return: A list containing zero or more idnums. If idnum is just a single
    number, then it will be returned inside a list. If there is an error,
    an empty list will be returned. If a range is specified, then multiple
    idnums will be returned in the list.

        For example: JB021-024 or JB021-24. These produce identical results:
        ['JB021', 'JB022', 'JB023', 'JB024']
    """
    jlist = []
    if '-' in idstr:  # if ID is actually a range like JB021-23
        if m := re.match(r'(.+?)(\d+)-(\d+)$', idstr):
            prefix = m[1]
            firstidnum = int(m[2])
            lastidnum = int(m[3])
            try:
                firstidlen = len(m[2])
                for suffix in range(firstidnum, lastidnum + 1):
                    newidnum = f'{prefix}{suffix:0{firstidlen}}'
                    jlist.append(newidnum)
            except ValueError:
                print(f'Bad accession number, contains "-" but not well'
                      f' formed: {m.groups()}')
        else:
            print('Bad accession number, failed pattern match:', idstr)
    else:
        jlist.append(idstr)
    return jlist


def read_include_list(includes_file, include_column, include_skip, verbos=1):
    """
    Read the optional CSV file from the --include argument. Build a list
    of accession IDs in upper case for use by cfgutil.select.
    :return: a set
    """

    if not includes_file:
        return None
    includeset = set()
    includereader = csv.reader(open(includes_file))
    for n in range(include_skip):  # default = 1
        skipped = next(includereader)  # skip header
        if verbos >= 1:
            print(f'Skipping row in "include" file: {skipped}')
    for row in includereader:
        idnum = row[include_column].upper()  # cfgutil.select needs uppercase
        idnumlist: list[str] = expand_idnum(idnum)
        if verbos >= 1:
            for num in idnumlist:
                if num in includeset:
                    print(f'Warning: Duplicate id number in include '
                          f'file, {num}, ignored.')
        includeset.update(idnumlist)  # one_idnum() returns a list
    return includeset
