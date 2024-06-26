#!/usr/local/bin/python3
"""
    Utility functions to convert spreadsheet notation to Python indices.
    Similar functions exist as xlrd.colname(56) => 'BE' and
    xlwt.rowcol_to_cell(5, 2) => 'C6'

"""

import string
import sys


def col2num(col: str | int | None) -> int | None:
    """
    Map a spreadsheet column to a zero-based index.
    If None, return None (useful with optional arguments) or a
    zero-based column number.

    :param col: either like 'A' (case-insensitive) or a number or None
                If a number is given it is a zero-based column number.
    :return: int | None
    """
    if col is None:
        return None
    if type(col) is int:
        return col
    if col.isnumeric():
        return int(col)
    num = 0
    for c in col.upper():
        if c in string.ascii_letters:
            num = num * 26 + (ord(c) - ord('A')) + 1
        else:
            raise ValueError('Column must be ASCII letters or positive '
                             f'numbers, not "{col}"')
    return num - 1


def num2col(num: int) -> str:
    """
    Map a zero-based index to a spreadsheet column.

    :param num: zero-based column number
    :return: a spreadsheet column letter or letters
    """
    s = ""
    num += 1
    while num > 0:
        module = (num - 1) % 26
        s = chr(ord('A') + module) + s
        num = int((num - module) / 26)
    return s


if __name__ == '__main__':
    if len(sys.argv) == 1:
        for ix in range(10000):
            # print ('ix', ix)
            nix = col2num(num2col(ix))
            if ix != nix:
                print('Failed. Input:', ix, 'Output:', nix)
                sys.exit()
        print('Passed.')
        sys.exit()

    arg = sys.argv[1]
    if arg.isdigit():
        print(num2col(int(arg)))
    else:
        print(col2num(arg))
