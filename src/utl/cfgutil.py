# -*- coding: utf-8 -*-
"""

"""

from collections import namedtuple
import yaml

Cfg = namedtuple('Cfg', ('columns', 'required'))


def mak_yaml_target(col):
    command, target, attrib = col
    if command == 'attrib':
        target += '@' + attrib
    elif command == 'count':
        target = f'{target}(len)'
        # print(target)
    elif command == 'ifattrib':
        return None  # Not included in heading
    h = target.split('/')[-1]  # trailing element name
    target = h.split('[')[0]  # strip trailing [@xyz='def']
    return target


def read_yaml_cfg(cfgf):
    genyaml = yaml.safe_load_all(cfgf)  # generator object
    cfg = [x for x in genyaml]
    for stmt in cfg:
        if 'title' not in stmt:
            stmt['title'] = mak_yaml_target((stmt['cmd'], stmt['elt'],
                                      stmt['attribute'] if 'attribute' in stmt else None))
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
            if command in ('column', 'count'):
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
