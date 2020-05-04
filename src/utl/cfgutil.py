# -*- coding: utf-8 -*-
"""
The configuration consists of a YAML file broken into multiple documents, separated by
lines containing "---" in the left three columns. Each document contains some of the
following statements. Statements are case sensitive; all must be lower case. Commands
can be column-generating or control statements.

Statements:
-----------
cmd            Required. See below for a description of the individual commands.
xpath          Required. This describes the XSLT path to a relevant XML element.
attribute      Required by the attrib and ifattrib commands.
title          Optional. If omitted, a best-guess title will be created from the xpath
               statement. If in a control document, this will be shown in diagnostics.
value          Required for ifeq or ifattrib or ifcontains command.
skip_number**  Do not write the ID number as the first column. This can be useful when
               sorting on another column.
record_tag**   This is the tag (of which there are usually many) that will be
               the root for extracting columns. The default is 'Object'.
record_id**    This is where the ID is found based on the root tag. The
               default is './ObjectIdentity/Number'.
normalize      Adjust this ID number so that it sorts in numeric order.
casesensitive  By default, comparisons are case insensitive.
width          truncate this column to this number of characters

Commands:
---------
attrib        Like column except displays the value of the named attribute.
column        This is the basic command to display the text of an element.
count         Displays the number of occurrences of an element under its parent.
global*       This document contains statements that affect the overall output,
              not just a specific column.
if*           Control command that selects an object to display if the element
              text is populated.
ifattrib*     Like if except tests for an attribute
ifattribeq*   Like ifeq except compares the value against an attribute
ifcontains*   Select an object if the value in the value statement is contained
              in the element text.
ifeq*         Select an object if the element text equals the value statement text.

*  These command do not generate output columns.
** These statements are only valid if the command is "global".

"""

import yaml

# The difference between the 'attrib' command and the attribute statement:
# The 'attrib' command is just like the column command except that the attribute
# value as given in the attribute statement is extracted.
# The 'attribute' statement is also used in the case of the 'ifattrib' command to name
# the attribute to test against the 'value' statement.


class Cmd:
    ATTRIB = 'attrib'
    COLUMN = 'column'
    COUNT = 'count'
    GLOBAL = 'global'
    IF = 'if'  # if text is present
    IFATTRIB = 'ifattrib'  # requires attribute statement
    IFATTRIBEQ = 'ifattribeq'  # requires attribute statement
    IFCONTAINS = 'ifcontains'
    IFEQ = 'ifeq'  # if the elt text equals the value statement
    IFSERIAL = 'ifserial'
    # Commands that do not produce a column in the output CSV file
    CONTROL_CMDS = (IF, IFEQ, IFATTRIB, IFSERIAL, GLOBAL, IFCONTAINS,
                    IFATTRIBEQ)
    NEEDVALUE_CMDS = (IFEQ, IFATTRIBEQ, IFSERIAL, IFCONTAINS)
    NEEDXPATH_CMDS = (ATTRIB, COLUMN, IF, COUNT, IFEQ, IFCONTAINS, IFATTRIB,
                      IFATTRIBEQ)


class Stmt:
    CMD = 'cmd'
    XPATH = 'xpath'
    ATTRIBUTE = 'attribute'
    TITLE = 'title'
    VALUE = 'value'
    CASESENSITIVE = 'casesensitive'
    NORMALIZE = 'normalize'
    WIDTH = 'width'
    SKIP_NUMBER = 'skip_number'
    RECORD_TAG = 'record_tag'
    RECORD_ID = 'record_id'


class Config:
    __instance = None

    @staticmethod
    def get_config():
        if Config.__instance is None:
            raise Exception('Config instance not created.')
        return Config.__instance

    def __init__(self, yamlcfgfile, title=False, dump=False):
        if Config.__instance is not None:
            raise ValueError("This class is a singleton!")
        Config.__instance = self
        self.col_docs = []  # documents that generate columns
        self.ctrl_docs = []  # control documents
        self.skip_number = False
        self.record_tag = 'Object'
        self.record_id = './ObjectIdentity/Number'
        self.norm = []  # True if this column needs to normalized/unnormalized
        cfglist = _read_yaml_cfg(yamlcfgfile, title=title, dump=dump)
        valid = validate_yaml_cfg(cfglist)
        if not valid:
            raise ValueError('Config failed validation.')
        for document in cfglist:
            cmd = document[Stmt.CMD]
            if cmd in Cmd.CONTROL_CMDS:
                if cmd == Cmd.GLOBAL:
                    for stmt in document:
                        if stmt == Stmt.CMD:
                            continue
                        elif stmt == Stmt.SKIP_NUMBER:
                            self.skip_number = True
                        elif stmt == Stmt.RECORD_ID:
                            self.record_id = document[stmt]
                        elif stmt == Stmt.RECORD_TAG:
                            self.record_tag = document[stmt]
                        else:
                            print(f'Unknown statement, ignored: {stmt}.')
                    continue
                else:  # not global
                    self.ctrl_docs.append(document)
            else:  # not control command
                self.col_docs.append(document)
        if not self.skip_number:
            self.norm.append(True)  # for the Serial number
        for doc in self.col_docs:
            self.norm.append(Stmt.NORMALIZE in doc)
        self.lennorm = len(self.norm)


def dump_document(document):
    print('Document:')
    for stmt in document:
        print(f'     {stmt}: {document[stmt]}')
    print('     ---')


def validate_yaml_cmd(cmd):
    validlist = [getattr(Cmd, c) for c in dir(Cmd)
                 if isinstance(getattr(Cmd, c), str) and not c.startswith('_')
                 ]
    # print('validlist', validlist)
    valid = cmd in validlist
    if not valid:
        print(f'{cmd} is not a valid command.')
    return valid


def validate_yaml_stmts(document):
    validlist = [getattr(Stmt, stmt) for stmt in dir(Stmt) if not stmt.startswith('_')]
    valid = True
    for stmt in document:
        if stmt not in validlist:
            print(f'"{stmt}" is not a valid statement.')
            valid = False
    return valid


def validate_yaml_cfg(cfglist):
    valid = True
    for document in cfglist:
        valid_doc = True
        if not validate_yaml_stmts(document):
            valid_doc = False
        if Stmt.CMD not in document:
            print('cmd statement is missing.')
            valid = False
            dump_document(document)
            break
        command = document[Stmt.CMD]
        if not validate_yaml_cmd(command):
            valid_doc = False
        if command in Cmd.NEEDXPATH_CMDS and Stmt.XPATH not in document:
            print(f'XPATH statement missing, cmd: {command}')
            valid_doc = False
        if command in Cmd.NEEDVALUE_CMDS and Stmt.VALUE not in document:
            print(f'value is required for {command} command.')
            valid_doc = False
        if command in (Cmd.ATTRIB, Cmd.IFATTRIB, Cmd.IFATTRIBEQ):
            if Stmt.ATTRIBUTE not in document:
                print(f'attribute is required for {command} command.')
                valid_doc = False
        if not valid_doc:
            valid = False
            dump_document(document)

    return valid


def _read_yaml_cfg(cfgf, title=False, dump=False):
    # Might be None for an empty document, like trailing "---"
    cfg = [c for c in yaml.safe_load_all(cfgf) if c is not None]
    for document in cfg:
        if dump:
            dump_document(document)
        cmd = document[Stmt.CMD]
        if cmd in Cmd.CONTROL_CMDS:
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


def select(elem, config):
    """

    :param elem: the Object element
    :param config: the YAML configuration, a list of dicts
    :return: selected is true if the Object element should be written out

    """

    selected = True
    for document in config.ctrl_docs:
        command = document[Stmt.CMD]
        if command == Cmd.GLOBAL:
            continue
        eltstr = document.get(Stmt.XPATH)
        if eltstr:
            element = elem.find(eltstr)
        else:
            element = None
        if element is None:
            selected = False
            break
        if command in (Cmd.ATTRIB, Cmd.IFATTRIB, Cmd.IFATTRIBEQ):
            attribute = document[Stmt.ATTRIBUTE]
            text = element.get(attribute)
        elif element.text is None:
            text = ''
        else:
            text = element.text.strip()
        if not text and command in (Cmd.IF, Cmd.IFATTRIB, Cmd.IFCONTAINS,
                                    Cmd.IFEQ, Cmd.IFATTRIBEQ):
            selected = False
            break
        if command in (Cmd.IFEQ, Cmd.IFCONTAINS, Cmd.IFATTRIBEQ):
            value = document[Stmt.VALUE]
            textvalue = text
            if Stmt.CASESENSITIVE not in document:
                value = value.lower()
                textvalue = textvalue.lower()
            if command == Cmd.IFCONTAINS and value not in textvalue:
                selected = False
                break
            elif command in (Cmd.IFEQ, Cmd.IFATTRIBEQ) and value != textvalue:
                selected = False
                break
            continue
    return selected


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
