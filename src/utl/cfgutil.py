# -*- coding: utf-8 -*-
"""
The configuration consists of a YAML file broken into multiple documents, separated by
lines containing just "---" in the left three columns. Each document contains some of the
following statements. Statements are case sensitive; all must be lower case. Commands
can be column-generating or control statements.

Statements:
-----------
cmd           Required. See below for a description of the individual commands.
elt           Required. This describes the XSLT path to a relevant XML element.
attribute     Required by the attrib and ifattrib commands.
title         Optional for column-generating commands. If omitted, a best-guess title will
              be created from the elt statement.
value         Required for ifeq or ifattrib command.
normalize     Adjust this ID number so that it sorts in numeric order.
casesensitive By default, comparisons are case insensitive.
width         truncate columns to this width

Commands:
---------
column        This is the basic command to display the text of an element
attrib        Like column except displays the value of the named attribute.
if            Control command that selects an object to display if the element text is
              populated.
ifeq          Select an object if the element text equals the value statement text
ifattrib      Like ifeq except compares the value against an attribute
count         Displays the number of occurrences of an element under its parent


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
    IFEQ = 'ifeq'  # requires value statement
    IFATTRIB = 'ifattrib'
    # Commands that do not produce a column in the output CSV file
    CONTROL_CMDS = (IF, IFEQ, IFATTRIB, GLOBAL)


class Stmt:
    CMD = 'cmd'
    ELT = 'elt'
    ATTRIBUTE = 'attribute'
    TITLE = 'title'
    VALUE = 'value'
    CASESENSITIVE = 'casesensitive'
    NORMALIZE = 'normalize'
    WIDTH = 'width'
    INHIBIT_NUMBER = 'inhibit_number'


Cfg = namedtuple('Cfg', ('column', 'required'))


def dump_document(document):
    print('Document:')
    for stmt in document:
        print(f'     {stmt}: {document[stmt]}')
    print('     ---')


def validate_yaml_cmd(cmd):
    validlist = [getattr(Cmd, c) for c in dir(Cmd) if isinstance(getattr(Cmd, c), str)
                 and not c.startswith('_')]
    # print('validlist', validlist)
    valid = cmd in validlist
    if not valid:
        print(f'{cmd} is not a valid command.')
    return valid


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
        if Stmt.ELT not in document and command != Cmd.GLOBAL:
            print(f'ELT statement missing, cmd: {command}')
            valid_doc = False
        if not validate_yaml_cmd(command):
            valid_doc = False
        if command in Cmd.CONTROL_CMDS:
            if Stmt.TITLE in document:
                print(f'title is illegal for {command} command.')
                valid_doc = False
        if command in (Cmd.IFEQ, Cmd.IFATTRIB):
            if Stmt.VALUE not in document:
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
    elif command in Cmd.CONTROL_CMDS:
        return None  # Not included in heading
    # command is 'column'
    h = target.split('/')[-1]  # trailing element name
    target = h.split('[')[0]  # strip trailing [@xyz='def']
    return target


def yaml_global(config):
    """

    :param config:
    :return: The global statements or None if none exist
    """

    for document in config:
        if document[Stmt.CMD] == Cmd.GLOBAL:
            global_stmts = {}
            for stmt in document:
                global_stmts[stmt] = document[stmt]
            return global_stmts


def read_yaml_cfg(cfgf, dump=False):
    # Might be None for an empty document, like trailing "---"
    cfg = [c for c in yaml.safe_load_all(cfgf) if c is not None]
    for document in cfg:
        cmd = document[Stmt.CMD]
        elt = document.get(Stmt.ELT)
        # Specify the column title. If the command 'title' isn't specified, construct
        # the title from the trailing element name from the 'elt' command.
        if 'title' not in document and cmd not in Cmd.CONTROL_CMDS:
            target = mak_yaml_col_hdg(cmd, elt, document.get('attrib'))
            if target:
                document[Stmt.TITLE] = target
        if dump:
            dump_document(document)
    return cfg


def read_cfg(cfgf):
    """
    :param cfgf: iterable (usually a file) containing lines of the form:
                 column <xpath statement>
                 count  <xpath statement>
                 attrib <xpath statement>, <attribute name>
                 required <xpath statement>
            where the xpath statement points to an xml element within the file
            The value returned may be None.

            The command "attrib" is like "column" except instead of returning
            the element's text, it returns the value of the named attribute.

            The command "count" returns the number of occurrences of that
            sub-element.

    :return: a Cfg namedtuple containing two members:
            First member:
            a list of 3-tuples containing:
                (0) the command name
                (1) xpath statements which will be used to extract
                    text values from an xml element.
                (2) * In case of an attrib command, the attribute name whose
                      value should be returned instead of the element's text
                      value.
                    * In case of a count command, optionally the minimum number
                      of occurrences required for this line to be output.
                    * If no parameter is required, None is returned as the
                      third parameter.

            Second member:
            a list of "required" statements such that only an element with that
                field populated will be included in the output
            If cfgf is None, return a Cfg namedtuple with empty lists.

    """
    cfg = []
    cols = []
    reqd = []
    if cfgf:
        for line in cfgf:
            line = line.strip()
            if not line or line[0] == '#':
                continue
            row = line.split(None, 1)
            assert len(row) > 1, f'Invalid command: "{line}"'
            command = row[0].lower()
            if command in (Cmd.COLUMN, Cmd.COUNT):
                row[1] = row[1].strip('\'"')  # remove leading & trailing quotes
                cols.append((command, row[1], None))
            elif command == 'required':
                reqd.append(row[1])
            elif command in ('attrib', 'ifattrib'):
                params = [command] + row[1].split(',')
                params = [x.strip() for x in params]
                if len(params) != 3:
                    raise SyntaxError(f'Bad number of parameters in ATTRIB'
                                      f' statement: "{line}".')
                cols.append(params)
            else:
                raise SyntaxError(f'Unknown command: {command}.')
        cfg = Cfg(cols, reqd)
    return cfg


def mak_yaml_target(col):
    title = col.get(Stmt.TITLE)
    if title:
        return title
    command = col[Stmt.CMD]
    target = col.get(Stmt.ELT)
    if target is None:
        return ""
    attrib = col.get(Stmt.ATTRIBUTE)
    if command == Cmd.ATTRIB:
        target += '@' + attrib
    elif command == 'count':
        target = f'{target}(len)'
        # print(target)
    return target


def maktarget(col):
    command, target, attrib = col
    if command == 'attrib':
        target += '@' + attrib
    elif command == 'count':
        target = f'{target}(len)'
        # print(target)
    elif command == 'ifattrib':
        return None  # Not included in heading
    return target


def yaml_fieldnames(cols):
    """
    :param cols: the list produced by read_cfg or that list converted to
                 a list of strings.
    :return: a list of column headings extracted from the last subelement in
             the xpath statement
    """
    hdgs = ['Serial']  # hardcoded first entry
    targets = [mak_yaml_target(col) for col in cols if col['cmd'] not in Cmd.CONTROL_CMDS]
    for col in targets:
        if col.startswith('.'):  # extract heading from elt statement
            h = col.split('/')[-1]  # trailing element name
            hdgs.append(h.split('[')[0])  # strip trailing [@xyz='def']
        else:
            hdgs.append(col)  # heading from title statement
    return hdgs


def fieldnames(cols):
    """
    :param cols: the list produced by read_cfg or that list converted to
                 a list of strings.
    :return: a list of column headings extracted from the last subelement in
             the xpath statement
    """
    hdgs = ['Serial']  # hardcoded first entry
    targets = [maktarget(col) for col in cols]
    for col in targets:
        if col:
            h = col.split('/')[-1]  # trailing element name
            hdgs.append(h.split('[')[0])  # strip trailing [@xyz='def']
    return hdgs
