# -*- coding: utf-8 -*-
"""

"""

from collections import namedtuple

Cfg = namedtuple('Cfg', ('columns', 'required'))


def read_cfg(cfgf):
    """
    :param cfgf: file containing lines of the form:
                 column <xpath statement>
                 required <xpath statement>
           where the xpath statement points to an xml element within the file
           The value may be None.

    :return: a Cfg namedtuple containing:
            a list of xpath statements which will be used to extract text
                values from an xml element.
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
            if len(row) > 1:
                row[1] = row[1].strip('\'"')  # remove leading & trailing quotes
            if row[0].lower() == 'column':
                cols.append(row[1])
            if row[0].lower() == 'required':
                reqd.append(row[1])
    cfg = Cfg(cols, reqd)
    return cfg


def fieldnames(cols):
    """
    :param cols: the list produced by read_cfg
    :return: a list of column headings extracted from the last subelement in
             the xpath statement
    """
    hdgs = ['Serial']  # hardcoded first entry
    for col in cols:
        h = col.split('/')[-1]  # trailing element name
        hdgs.append(h.split('[')[0])  # strip trailing [@xyz='def']
    return hdgs
