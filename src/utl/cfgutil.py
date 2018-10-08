# -*- coding: utf-8 -*-
"""

"""


def read_cfg(cfgf):
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
    hdgs = ['Serial']
    for col in cols:
        h = col.split('/')[-1]  # trailing element name
        hdgs.append(h.split('[')[0])  # strip trailing [@xyz='def']
    return hdgs
