# -*- coding: utf-8 -*-
"""
    Create a report of box contents with columns for the stocktake.
    Parameters:
        1. Input XML file. This is a Modes database.
        2. Output CSV file.
"""
import argparse
import codecs
from collections import defaultdict
import csv
import io
import re
import sys

from utl.cfgutil import Config, Stmt
from utl.normalize import sphinxify, normalize_id
from utl.readers import object_reader


CFG_STRING = """
---
# cmd: column
# xpath: ./ObjectLocation[@elementtype="current location"]/Location
# title: Current
# ---
cmd: column
xpath: ./ObjectLocation[@elementtype="normal location"]/Location
title: Normal
---
cmd: column
xpath: ./Identification/Title
width: 40
"""


def pad_loc(loc):
    """
    If the location field matches the pattern "<Letter(s)><Number(s)>" like
    "S1" then pad the number part so that it sorts correctly. Also convert the
    letter part to upper case
    :param loc: location
    :return: padded location
    """
    m = re.match(r'(\D+)(\d+)', loc)
    if m:
        g1 = m.group(1).upper()
        g2 = int(m.group(2))
        return f'{g1}{g2:03}'
    else:
        return loc


def unpad_loc(loc):
    m = re.match(r'(\D+)(\d+)', loc)
    if m:
        g1 = m.group(1).upper()
        g2 = int(m.group(2))
        return f'{g1}{g2}'
    else:
        return loc


def one_xml_object(elt):
    num = elt.find('./ObjectIdentity/Number').text
    loc = elt.find('./ObjectLocation[@elementtype="current location"]/Location')
    if loc is not None and loc.text:
        location = pad_loc(loc.text)
    else:
        location = 'unknown'
    row = [num]
    for doc in cfg.col_docs:
        xpath = doc[Stmt.XPATH]
        data = elt.find(xpath)
        if data is not None and data.text:
            datatext = data.text
        else:
            datatext = 'unknown'
        if Stmt.WIDTH in doc:
            datatext = datatext[:int(doc[Stmt.WIDTH])]
        row.append(datatext)
    boxdict[location].append(row)


def main(config):
    for _, elt in object_reader(_args.infile, config=config):
        one_xml_object(elt)
        elt.clear()
    for box in sorted(boxdict.keys()):
        writer.writerow([''])
        # writer.writerow([''])
        # writer.writerow(['Box', unpad_loc(box)])
        # writer.writerow(['--------------'])
        writer.writerow([f'Box {unpad_loc(box)}'] + [doc['title'] for doc in cfg.col_docs])
        for row in sorted(boxdict[box], key=lambda x: normalize_id(x[0])):
            writer.writerow(row)


def getparser() -> argparse.ArgumentParser:
    """
    Called either by getargs() in this file or by Sphinx.
    :return: an argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser(description='''
        Create a report of box contents with columns for the stocktake. The
        script uses a configuration file embedded in the Python code.''')
    parser.add_argument('infile', help=sphinxify('''
        Modes XML database file or CSV file.
        ''', called_from_sphinx))
    parser.add_argument('outcsv', help='''
        The output CSV file.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary
        information.''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


called_from_sphinx = True


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    called_from_sphinx = False
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    cfg_file = io.StringIO(CFG_STRING)
    cfg = Config(cfg_file, dump=_args.verbose > 1)
    outcsv = codecs.open(_args.outcsv, 'w', 'utf-8-sig')
    writer = csv.writer(outcsv)
    boxdict = defaultdict(list)
    main(cfg)
