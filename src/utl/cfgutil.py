# -*- coding: utf-8 -*-
"""
The configuration consists of a YAML file broken into multiple documents, separated by
lines containing just "---" in the left three columns. Each document contains some of the
following statements. Statements are case sensitive; all must be lower case. Commands
can be column-generating or control statements.

Statements:
-----------
cmd            Required. See below for a description of the individual commands.
xpath          Required. This describes the XSLT path to a relevant XML element.
attribute      Required by the attrib and ifattrib commands.
title          Optional. If omitted, a best-guess title will be created from the elt
               statement. If in a control document, this will be shown in diagnostics.
value          Required for ifeq or ifattrib or ifcontains command.
skip_number    Do not write the ID number as the first column. This can be useful when
               sorting on another column. Include this statement under a global
               command.
normalize      Adjust this ID number so that it sorts in numeric order.
casesensitive  By default, comparisons are case insensitive.
width          truncate columns to this width

Commands:
---------
attrib        Like column except displays the value of the named attribute.
column        This is the basic command to display the text of an element
count         Displays the number of occurrences of an element under its parent
global*       Contains statements that affect the overall output, not just a
              specific column.
if*           Control command that selects an object to display if the element text is
              populated.
ifattrib*     Like ifeq except compares the value against an attribute
ifcontains*   Select an object if the value in the value statement is contained
              in the element text.
ifeq*         Select an object if the element text equals the value statement text.

* These command do not generate output columns.

"""

from collections import namedtuple
import yaml

# The difference between the 'attrib' command and the attribute statement:
# The 'attrib' command is just like the column command except that the attribute
# value as given in the attribute statement is extracted.
# The 'attribute' statement is also used in the case of the 'ifattrib' command to name the
# attribute to test against the 'value' statement.


class Cmd:
    ATTRIB = 'attrib'
    COLUMN = 'column'
    GLOBAL = 'global'
    IF = 'if'  # if text is present
    COUNT = 'count'
    IFEQ = 'ifeq'  # if the elt text equals the value statement
    IFCONTAINS = 'ifcontains'
    IFATTRIB = 'ifattrib'  # requires attribute statement
    IFSERIAL = 'ifserial'
    # Commands that do not produce a column in the output CSV file
    CONTROL_CMDS = (IF, IFEQ, IFATTRIB, IFSERIAL, GLOBAL, IFCONTAINS)
    NEEDVALUE_CMDS = (IFEQ, IFATTRIB, IFSERIAL, IFCONTAINS)
    NEEDELT_CMDS = (ATTRIB, COLUMN, IF, COUNT, IFEQ, IFCONTAINS, IFATTRIB, )


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


class Config:
    __instance = None

    @staticmethod
    def get_config():
        if Config.__instance is None:
            raise Exception('Config instance not created.')
        return Config.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Config.__instance is not None:
            raise Exception("This class is a singleton!")
        Config.__instance = self
        col_docs = []  # documents that generate columns
        cmd_docs = []  # control documents
        


def validate_yaml_cmd(cmd):
    validlist = [getattr(Cmd, c) for c in dir(Cmd) if isinstance(getattr(Cmd, c), str)
                 and not c.startswith('_')]
    # print('validlist', validlist)
    valid = cmd in validlist
    if not valid:
        print(f'{cmd} is not a valid command.')
    return valid


def dump_document(document):
    print('Document:')
    for stmt in document:
        print(f'     {stmt}: {document[stmt]}')
    print('     ---')


def validate_yaml_stmts(document):
    validlist = [getattr(Stmt, stmt) for stmt in dir(Stmt) if not stmt.startswith('_')]
    # print(validlist)
    # print(document)
    valid = True
    for stmt in document:
        if stmt not in validlist:
            print(f'"{stmt}" is not a valid statement.')
            valid = False
    return valid


def validate_yaml_cfg(cfg):
    valid = True
    for document in cfg:
        valid_doc = True
        if not validate_yaml_stmts(document):
            valid_doc = False
        command = document[Stmt.CMD] if Stmt.CMD in document else None
        if command is None:
            print('cmd statement is missing.')
            valid = False
            dump_document(document)
            break
        if command in Cmd.NEEDELT_CMDS and Stmt.XPATH not in document:
            print(f'XPATH statement missing, cmd: {command}')
            valid_doc = False
        if not validate_yaml_cmd(command):
            valid_doc = False
        if command in Cmd.NEEDVALUE_CMDS and Stmt.VALUE not in document:
            print(f'value is required for {command} command.')
            valid_doc = False
        if command in (Cmd.ATTRIB, Cmd.IFATTRIB):
            if Stmt.ATTRIBUTE not in document:
                print(f'attribute is required for {command} command.')
                valid_doc = False
        if not valid_doc:
            valid = False
            dump_document(document)

    return valid


def mak_yaml_col_hdg(command, target, attrib):
    if command == Cmd.ATTRIB:
        target += '@' + attrib
    elif command == Cmd.COUNT:
        target = f'{target}(len)'
        # print(target)
    elif target is None:
        return None  # Not included in heading
    # command is 'column'
    h = target.split('/')[-1]  # trailing element name
    target = h.split('[')[0]  # strip trailing [@xyz='def']
    return target


def yaml_global(config):
    """
    :param config:
    :return: A dict containing the global statements
    """

    global_stmts = {}
    for document in config:
        if document[Stmt.CMD] == Cmd.GLOBAL:
            for stmt in document:
                global_stmts[stmt] = document[stmt]
    return global_stmts


def read_yaml_cfg(cfgf, title=False, dump=False):
    # Might be None for an empty document, like trailing "---"
    cfg = [c for c in yaml.safe_load_all(cfgf) if c is not None]
    for document in cfg:
        cmd = document[Stmt.CMD]
        elt = document.get(Stmt.XPATH)
        # Specify the column title. If the command 'title' isn't specified,
        # construct the title from the trailing element name from the 'elt'
        # statement. The validate_yaml_cfg function checks that the elt
        # statement is there if needed.
        if title and 'title' not in document and elt is not None:
            document[Stmt.TITLE] = mak_yaml_col_hdg(cmd, elt, document.get('attrib'))
        if dump:
            dump_document(document)
    return cfg


def yaml_fieldnames(cols):
    """
    :param cols: the list produced by read_cfg or that list converted to
                 a list of strings.
    :return: a list of column headings extracted from the last subelement in
             the xpath statement
    """
    hdgs = ['Serial']  # hardcoded first entry
    titles = [col[Stmt.TITLE] for col in cols if col[Stmt.CMD] not in Cmd.CONTROL_CMDS]
    for col in titles:
        if col.startswith('.'):  # extract heading from elt statement
            h = col.split('/')[-1]  # trailing element name
            hdgs.append(h.split('[')[0])  # strip trailing [@xyz='def']
        else:
            hdgs.append(col)  # heading from title statement
    return hdgs


