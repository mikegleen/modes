# -*- coding: utf-8 -*-
"""

"""


def read_cfg(cfgf):
    """
    :param cfgf: file containing lines of the form:
                 column <xpath statement>
           where the xpath statement points to an xml element with the text
           that we want to extract
    :return: a list of xpath statements which will be used to extract text
             values from an xml element.
    """
    cols = []
    for line in cfgf:
        line = line.strip()
        if not line or line[0] == '#':
            continue
        row = line.split(None, 1)
        if len(row) > 1:
            row[1] = row[1].strip('\'"')  # remove leading & trailing quotes
        if row[0].lower() == 'column':
            cols.append(row[1])
    return cols


def fieldnames(cols):
    """
    :param cols: the list produced by read_cfg
    :return: a list of column headings extracted from the last subelement in
             the xpath statement
    """
    hdgs = ['Serial']
    for col in cols:
        h = col.split('/')[-1]  # trailing element name
        hdgs.append(h.split('[')[0])  # strip trailing [@xyz='def']
    return hdgs
