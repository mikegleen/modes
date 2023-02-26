"""

"""
import codecs
import csv
import os
import sys
from openpyxl import load_workbook
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import Config
from utl.zipmagic import openfile


def trimrow(r: list, maxlen: int):
    """

    :param r:
    :param maxlen:
    :return: Trailing blank cells are removed from the list
    """
    ix = len(r) - 1
    while len(r) > maxlen:
        if r[ix]:
            break
        r.pop()
        ix -= 1


def object_reader(infilename: str | None, config=None, verbos=1):
    """

    :param infilename: The XML file in Modes format
    :param config: A Config object or None in which case an empty one is made
    :param verbos: trace level
    :return: A tuple of (accession number, element)
    """
    objectlevel = 0
    if config is None:
        config = Config()
    with openfile(infilename) as infile:
        for event, elem in ET.iterparse(infile, events=('start', 'end')):
            # print(event)
            if event == 'start':
                # print(elem.tag)
                if elem.tag == config.record_tag:
                    objectlevel += 1
                continue
            # It's an "end" event.
            if elem.tag != config.record_tag:  # default: Object
                continue
            objectlevel -= 1
            if objectlevel:
                continue  # It's not a top level Object.
            data = []
            idelem = elem.find(config.record_id_xpath)
            idnum = idelem.text if idelem is not None else ''
            if verbos >= 3:
                print('idnum: {}', idnum)
            yield idnum, elem


def row_dict_reader(filename: str | None, verbos=1, skiprows=0,
                    allow_long_rows=False):
    """
    A generator function to iterate through either a CSV file or XLSX file.

    We only look at the first sheet of an XLSX file.

    :param filename:
    :param verbos:
    :param skiprows:
    :param allow_long_rows:
    :return: an iterator that calls this function or None
    """
    if not filename:
        return None
    _, suffix = os.path.splitext(filename)
    if suffix.lower() == '.csv':
        with codecs.open(filename, 'r', 'utf-8-sig') as mapfile:
            for _ in range(skiprows):
                next(mapfile)
            reader = csv.DictReader(mapfile)
            n_input_fields = len(reader.fieldnames)
            if verbos >= 1:
                print(f'CSV Column Headings: {", ".join(reader.fieldnames)}')
            for nrow, row in enumerate(reader):
                if not allow_long_rows and len(row) > n_input_fields:
                    print(f"Error: row {nrow + 1} longer than heading: {row}")
                    sys.exit(1)
                yield row
    elif suffix.lower() == '.xlsx':
        wb = load_workbook(filename=filename)
        ws = wb.active
        enumrows = enumerate(ws.iter_rows(values_only=True))
        for _ in range(skiprows):
            next(enumrows)
        _, heading = next(enumrows)
        heading = list(heading)  # tuple -> list so it can be trimmed
        trimrow(heading, 0)
        # print(len(heading))
        # sys.exit()
        n_input_fields = len(heading)
        if verbos >= 1:
            print(f'Excel Column Headings: '
                  f'{", ".join([str(x) for x in heading])}')
        for nrow, rawrow in enumrows:
            rawrow = list(rawrow)
            row = dict()
            # print(f'before: {rawrow}')
            trimrow(rawrow, n_input_fields)
            # print(f'after : {rawrow}')
            if not allow_long_rows and len(rawrow) > n_input_fields:
                print(f"Error: row {nrow + 1} longer than heading: {rawrow}")
                sys.exit(1)
            for ncell, cell in enumerate(rawrow):
                if type(cell) == str:
                    cell = cell.replace('\n', ' ')
                row[heading[ncell]] = '' if cell is None else str(cell).strip()
            if not ''.join(row.values()):
                continue
            yield row
