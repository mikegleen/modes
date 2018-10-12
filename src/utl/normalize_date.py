# -*- coding: utf-8 -*-
"""
    Convert a datetime or date object to Modes format d[d].m[m].yyyy.
"""


def modesdate(indate):
    """
    :param indate: An object like a datetime or date that has month, day and
    year attributes.
    :return: a string in Modes format d[d].m[m].yyyy.
    """
    d = indate.day
    m = indate.month
    y = indate.year
    return f'{d}.{m}.{y}'
