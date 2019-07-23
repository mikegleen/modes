# -*- coding: utf-8 -*-
"""

"""

from collections import namedtuple

Cfg = namedtuple('Cfg', ('columns', 'required'))


def read_cfg(cfgf):
    """
    :param cfgf: file containing lines of the form:
                 column <xpath statement>
                 attrib <xpath statement>, <attribute name>
                 required <xpath statement>
            where the xpath statement points to an xml element within the file
            The value may be None.
            The command "attrib" is like "column" except instead of returning
            the element's text, it returns the value of the named attribute.

    :return: a Cfg namedtuple containing two members:
            First member:
            a list of either
                (1) xpath statements which will be used to extract
                text values from an xml element.
            or  (2) a two-element list containing the xpath statement as above
                and the attribute name whose value should be returned instead
                of the element's text value.
            The two types of members may be mixed.

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
            if command == 'column':
                row[1] = row[1].strip('\'"')  # remove leading & trailing quotes
                cols.append(row[1])
            elif command == 'required':
                reqd.append(row[1])
            elif command == 'attrib':
                params = row[1].split(',')
                params = [x.strip() for x in params]
                if len(params) != 2:
                    raise SyntaxError(f'Bad number of parameters in ATTRIB'
                                      f' statement: "{line}".')
                cols.append(params)
            else:
                raise SyntaxError(f'Unknown command: {command}.')
        cfg = Cfg(cols, reqd)
    return cfg


def fieldnames(cols):
    """
    :param cols: the list produced by read_cfg or that list converted to
                 a list of strings.
    :return: a list of column headings extracted from the last subelement in
             the xpath statement
    """
    hdgs = ['Serial']  # hardcoded first entry
    targets = [col if isinstance(col, str) else col[0] + '@' + col[1] for col
               in cols]
    for col in targets:
        h = col.split('/')[-1]  # trailing element name
        hdgs.append(h.split('[')[0])  # strip trailing [@xyz='def']
    return hdgs
