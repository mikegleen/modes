"""

"""
import os
import codecs
import csv
from openpyxl import load_workbook


def row_reader(filename, verbos=1, skiprows=0):
    """
    A generator function to iterate throw either a CSV file or XLSX file.

    We only look at the first sheet of an XLSX file.

    :param filename:
    :param verbos:
    :param skiprows:
    :return: an iterator that calls this function
    """
    _, suffix = os.path.splitext(filename)
    if suffix.lower() == '.csv':
        with codecs.open(filename, 'r', 'utf-8-sig') as mapfile:
            for _ in range(skiprows):
                next(mapfile)
            reader = csv.DictReader(mapfile)
            if verbos >= 1:
                print(f'CSV Column Headings: {reader.fieldnames}')
            for row in reader:
                yield row
    elif suffix.lower() == '.xlsx':
        wb = load_workbook(filename=filename)
        ws = wb.active
        enumrows = enumerate(ws.iter_rows(values_only=True))
        for _ in range(skiprows):
            next(enumrows)
        _, heading = next(enumrows)
        if verbos >= 1:
            print(f'Excel Column Headings: {heading}')
        for nrow, rawrow in enumrows:
            row = dict()
            for ncell, cell in enumerate(rawrow):
                if type(cell) == str:
                    cell = cell.replace('\n', ' ')
                row[heading[ncell]] = cell
            yield row

