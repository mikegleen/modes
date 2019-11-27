# -*- coding: utf-8 -*-
"""

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
    IF = 'if'  # if text is present
    COUNT = 'count'
    IFEQ = 'ifeq'  # requires value statement
    IFATTRIB = 'ifattrib'
    # Commands that do not produce a column in the output CSV file
    CONTROL_CMDS = (IF, IFEQ, IFATTRIB)


class Stmt:
    CMD = 'cmd'
    ELT = 'elt'
    ATTRIBUTE = 'attribute'
    TITLE = 'title'
    VALUE = 'value'
    CASESENSITIVE = 'casesensitive'


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
        command = document[Stmt.CMD]
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


def read_yaml_cfg(cfgf):
    cfg = list(yaml.safe_load_all(cfgf))
    for document in cfg:
        cmd = document[Stmt.CMD]
        elt = document[Stmt.ELT]
        # Specify the column title. If the command 'title' isn't specified, construct
        # the title from the trailing element name from the 'elt' command.
        if 'title' not in document:
            target = mak_yaml_col_hdg(cmd, elt, document.get('attrib'))
            if target:
                document[Stmt.TITLE] = target
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
    target = col[Stmt.ELT]
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
