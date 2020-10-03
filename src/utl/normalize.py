# -*- coding: utf-8 -*-
"""
    Convert a datetime or date object to Modes format d[d].m[m].yyyy.
"""
import datetime
import re


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


def normalize_id(objid, mdacode='LDHRM', verbose=1):
    """
    The parameter is a string in the format of one of the types of object
    identifiers in our Modes file.

    Return a string normalized for sorting.

    Input can be of the form JB001 or JB0001 or JB001a or SH1 or LDHRM/2018/1
    or LDHRM.2018.1. Input can also be a simple integer.
    """
    objid = objid.upper()
    if objid.startswith(mdacode):
        idlist = re.split(r'[/.]', objid)  # split on either "/" or "."
        assert len(idlist) == 3
        assert len(idlist[2]) <= 4
        idlist[2] = f'{int(idlist[2]):0>4d}'
        return '.'.join(idlist)
    # Not an LDHRM/.. id
    m = re.match(r'(\D+)(\d+)(.*)', objid)
    if m:
        newobjid = m.group(1) + f'{int(m.group(2)):08d}' + m.group(3)
        if verbose > 1:
            print(f'normalize: {objid} -> {newobjid}')
        return newobjid
    elif objid.isnumeric() and len(objid) <= 8:
        newobjid = f'{int(objid):08d}'
        if verbose > 1:
            print(f'normalize: {objid} -> {newobjid}')
        return newobjid
    raise ValueError(f'Unsupported accession ID format: {objid}')


def denormalize_id(objid, mdacode):
    if objid.startswith(mdacode):
        idlist = re.split(r'[/.]', objid)  # split on either "/" or "."
        assert len(idlist) == 3
        assert len(idlist[2]) <= 4
        idlist[2] = f'{int(idlist[2])}'
        return '.'.join(idlist)
    # Not an LDHRM/.. id
    m = re.match(r'(\D+)(\d+)(.*)', objid)
    if m:
        if objid.startswith('JB'):
            return m.group(1) + f'{int(m.group(2)):0>3d}' + m.group(3)
        else:
            return m.group(1) + f'{int(m.group(2))}' + m.group(3)
    elif objid.isnumeric():
        return objid.lstrip('0')
    else:
        return objid
