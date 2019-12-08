# -*- coding: utf-8 -*-
"""
    Convert a datetime or date object to Modes format d[d].m[m].yyyy.
"""
import datetime


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


def date(indate: str):
    """
        Return a datetime.date object from a string in Modes format which can be:
            d.m.yyyy
            or m.yyyy
            or yyyy
        If day or month aren't given, the default values are returned. The day and month
        should not have leading zeros.
    :param indate:
    :return: datetime.date if a valid date exists otherwise a ValueError is raised.
             A TypeError is raised if indate is None.
    """
    try:
        d = datetime.datetime.strptime(indate, '%d.%m.%Y').date()
    except ValueError:
        try:
            d = datetime.datetime.strptime(indate, '%m.%Y').date()
        except ValueError:
            d = datetime.datetime.strptime(indate, '%Y').date()
    return d


def vdate(indate: str):
    """
    This is similar to the date function above but more restrictive. It is used to
    validate that a string is a complete Modes format date.

    :param indate:
    :return: A datetime.datetime object or None if the string is not valid.
             A TypeError is raised if indate is None.
    """
    try:
        d = datetime.datetime.strptime(indate, '%d.%m.%Y').date()
    except ValueError:
        return None
    return d

