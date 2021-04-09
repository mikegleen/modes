# -*- coding: utf-8 -*-
"""
    Convert a datetime or date object to Modes format d[d].m[m].yyyy.
"""
import datetime
import re

DEFAULT_MDA_CODE = 'LDHRM'


def modesdate(indate: datetime.date, nfields: int = 3):
    """
    :param indate: An object like a datetime or date that has month, day and
    year attributes.
    :param nfields: Number of fields to write
    :return: a string in Modes format depending on the value of nfields:
             1 -> yyyy
             2 -> m[m].yyyy
             3 -> d[d].m[m].yyyy
    """
    d = indate.day
    m = indate.month
    y = indate.year
    if nfields == 3:
        return f'{d}.{m}.{y}'
    elif nfields == 2:
        return f'{m}.{y}'
    elif nfields == 1:
        return f'{y}'
    else:
        raise ValueError(f'Number of fields not in 1..3: {nfields}')


def modesdatefromisoformat(instr):
    """
    :param instr: A string in the format yyyy-mm-dd
    :return: a string in Modes format d[d].m[m].yyyy.
    """
    indate = datetime.date.fromisoformat(instr)
    d = indate.day
    m = indate.month
    y = indate.year
    return f'{d}.{m}.{y}'


def datefrommodes(indate: str) -> tuple[datetime.date, int]:
    """
        Parse a string in Modes format which can be:
            d.m.yyyy
            or m.yyyy
            or yyyy
        If day or month aren't given, the default values are returned. The day
        and month should not have leading zeros.
    :param indate:
    :return: A tuple containing datetime.date and a status if a valid date
             exists otherwise a ValueError is raised.
             A TypeError is raised if indate is None.
             A ValueError if the date format is not parseable.
             The status contains the number of parts found in the date.
    """
    try:
        d = datetime.datetime.strptime(indate, '%d.%m.%Y').date()
        nparts = 3
    except ValueError:
        try:
            d = datetime.datetime.strptime(indate, '%m.%Y').date()
            nparts = 2
        except ValueError:
            d = datetime.datetime.strptime(indate, '%Y').date()
            nparts = 1
    return d, nparts


def britishdatefrommodes(indate: str):
    """
    :param indate: A string containing a Modes date.
    :return: A string like "17 Aug 1909" or "Aug 1909" or "1909" or "unknown"
    """
    try:
        d, nparts = datefrommodes(indate)
    except ValueError:
        return 'unknown'
    if nparts == 1:
        return indate
    elif nparts == 2:
        return f'{d.strftime("%b %Y")}'
    elif nparts == 3:
        return f'{d.day} {d.strftime("%b %Y")}'  # no leading zero on day
    else:
        return 'unknown'


def vdate(indate: str):
    """
    This is similar to the date function above but more restrictive. It is used
    to validate that a string is a complete Modes format date.

    :param indate:
    :return: A datetime.date object or None if the string is not valid.
             A TypeError is raised if indate is None.
    """
    try:
        d = datetime.datetime.strptime(indate, '%d.%m.%Y').date()
    except ValueError:
        return None
    return d


def normalize_id(objid, mdacode=DEFAULT_MDA_CODE, verbose=1):
    """
    The parameter is a string in the format of one of the types of object
    identifiers in our Modes file.

    Return a string normalized for sorting.

    Input can be of the form JB001 or JB0001 or JB001a or SH1 or LDHRM/2018/1
    or LDHRM.2018.1. Input can also be a simple integer.
    """
    if objid is None:
        return None
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
        if verbose > 2:
            print(f'normalize: {objid} -> {newobjid}')
        return newobjid
    elif objid.isnumeric() and len(objid) <= 8:
        newobjid = f'{int(objid):08d}'
        if verbose > 2:
            print(f'normalize: {objid} -> {newobjid}')
        return newobjid
    raise ValueError(f'Unsupported accession ID format: {objid}')


def denormalize_id(objid, mdacode=DEFAULT_MDA_CODE):
    if objid.startswith(mdacode):
        idlist = re.split(r'[/.]', objid)  # split on either "/" or "."
        assert len(idlist) == 3
        assert len(idlist[2]) <= 4
        idlist[2] = f'{int(idlist[2])}'
        return '.'.join(idlist)
    # Not an LDHRM/.. id
    m = re.match(r'(\D+)(\d+)(.*)', objid)
    if m:
        if objid.startswith('JB'):  # pad with leading zeroes to 3 columns
            return m.group(1) + f'{int(m.group(2)):0>3d}' + m.group(3)
        else:
            return m.group(1) + f'{int(m.group(2))}' + m.group(3)
    elif objid.isnumeric():
        return objid.lstrip('0')
    else:
        return objid


if __name__ == '__main__':
    print('This module is not callable. Try src/normalize_xml.py')
