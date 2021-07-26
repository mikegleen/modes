# -*- coding: utf-8 -*-
"""
    Convert a datetime or date object to Modes format d[d].m[m].yyyy.
"""
import datetime
import re

DEFAULT_MDA_CODE = 'LDHRM'
MODESTYPE = 'modestype'
BRITISHTYPE = 'britishtype'


def modesdate(indate: datetime.date, nfields: int = 3) -> str:
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


def isoformatfrommodesdate(instr):
    dfm, _ = datefrommodes(instr)
    return dfm.isoformat()


def datefrommodes(indate: str) -> tuple[datetime.date, int]:
    """
        Parse a string in Modes format which can be:
            d.m.yyyy    (3 parts)
            or m.yyyy   (2 parts)
            or yyyy     (1 part)
        If day or month aren't given, the default values are returned. The day
        and month should not have leading zeros.
    :param indate:
    :return: A tuple containing datetime.date and a part count if a valid date
             exists otherwise a ValueError is raised.
             A TypeError is raised if indate is None.
             A ValueError if the date format is not parseable.
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


def datefrombritishdate(indate: str) -> tuple[datetime.date, int, str]:
    """
        Parse a string in Modes format (see datefrommodes) or
        a British date which can be:
            "d mmm yyyy"
            or "d month yyyy"
            or "mmm yyyy"
            or "month yyyy"
            It can also be yyyy but this is treated as Modes format.
        If day or month aren't given, the default values are returned.
    :param indate:
    :return: A tuple containing datetime.date and a part count followed by a
             date type indicator if a valid date exists otherwise a
             ValueError is raised.
             A TypeError is raised if indate is None.
             A ValueError if the date format is not parseable.
             The date type indicator contains 'modestype' if the date is Modes
             format and 'britishtype' if the date is British format.
    """

    try:
        d, nparts = datefrommodes(indate)
        return d, nparts, MODESTYPE
    except ValueError:
        pass
    try:  # 3 Mar 1917
        d = datetime.datetime.strptime(indate, '%d %b %Y').date()
        return d, 3, BRITISHTYPE
    except ValueError:
        pass
    try:  # 3 March 1917
        d = datetime.datetime.strptime(indate, '%d %B %Y').date()
        return d, 3, BRITISHTYPE
    except ValueError:
        pass
    try:
        d = datetime.datetime.strptime(indate, '%b %Y').date()
        return d, 2, BRITISHTYPE
    except ValueError as ve:
        pass
    try:
        d = datetime.datetime.strptime(indate, '%B %Y').date()
        return d, 2, BRITISHTYPE
    except ValueError as ve:
        raise ve


def britishdatefrommodes(indate: str) -> str:
    """
    :param indate: A string containing a Modes date.
    :return: A string like "17 Aug 1909" or "Aug 1909" or "1909" or "unknown"
    """
    try:
        d, nparts = datefrommodes(indate)
    except ValueError:
        return 'unknown'
    if nparts == 1:  # just the year
        return indate
    elif nparts == 2:
        return f'{d.strftime("%b %Y")}'
    elif nparts == 3:
        return f'{d.day} {d.strftime("%b %Y")}'  # no leading zero on day
    else:
        return 'unknown'


def modesdatefrombritishdate(indate: str) -> tuple[str, int, str]:
    """

    :param indate: A string in probably dd mmm yyyy but maybe modes format,
                   dd.mm.yyyy
    :return: A tuple of a string in Modes format, partcount, datetype where
             datetype is the original format, either MODESTYPE or BRITISHTYPE.
             It would be MODESTYPE if only the year was given.
    """
    newdate, partcount, datetype = datefrombritishdate(indate)
    if datetype == MODESTYPE:
        return indate, partcount, datetype
    mdate = modesdate(newdate, partcount)
    return mdate, partcount, datetype


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

    If a field that is expected to be an integer is not, a ValueError is
    raised.

    Input can be of the form JB001 or JB0001 or JB001a or SH1 or LDHRM/2018/1
    or LDHRM.2018.1. or LDHRM.2018.1.2. Input can also be a simple integer.

    For IDs with the MDA code, the one or two trailing numbers are expanded to
    six digits with leading zeroes if necessary. If an id contains a larger
    number an exception is raised. As a special case, JB numbers have a
    minimum of three digits which are expanded to six.
    For example:
    LDHRM.2018.1 -> LDHRM.2018.000001
    LDHRM.2018.1.2 -> LDHRM.2018.000001.000002
    JB001 -> JB00000001

    For IDs that are simple integers, these are expanded to eight digits.
    """
    if objid is None:
        return None
    objid = objid.upper()
    if objid.startswith(mdacode):
        idlist = re.split(r'[/.]', objid)  # split on either "/" or "."
        assert len(idlist) in (3, 4)
        assert len(idlist[2]) <= 6
        idlist[2] = f'{int(idlist[2]):06d}'
        if len(idlist) == 4:
            assert len(idlist[3]) <= 6
            idlist[3] = f'{int(idlist[3]):06d}'
        return '.'.join(idlist)
    # Not an LDHRM... id

    m = re.match(r'(\D+)(\d+)([A-Za-z]?)(\.(\d+))?$', objid)
    # On a successful match, this patten returns five groups. If there is
    # no subgroup ID, groups 4 and 5 will be None. We are not interested in
    # group 4 as it includes the '.' followed by the subgroup ID whereas group
    # 5 includes just the subgroup ID. So:
    # JB123 -> ('JB', '123', '', None, None)
    # JB123.2 -> ('JB', '123', '', '.2', '2')
    if m:
        assert len(m.group(2)) <= 6
        newobjid = m.group(1) + f'{int(m.group(2)):06d}' + m.group(3)
        # See if it has a sub-number, like JB124.23
        if m.group(5):
            assert len(m.group(5)) <= 6
            newobjid += '.' + f'{int(m.group(5)):06d}'
        if verbose > 2:
            print(f'normalize: {objid} -> {newobjid}')
        return newobjid
    elif objid.isnumeric() and len(objid) <= 6:
        newobjid = f'{int(objid):06d}'
        if verbose > 2:
            print(f'normalize: {objid} -> {newobjid}')
        return newobjid
    raise ValueError(f'Unsupported accession ID format: {objid}')


def denormalize_id(objid, mdacode=DEFAULT_MDA_CODE):
    """
    :param objid: A normalized accession number
    :param mdacode: Usually LDHRM
    :return: An accession number with leading zeroes removed from numeric
             fields.
    """
    if objid.startswith(mdacode):
        idlist = re.split(r'[/.]', objid)  # split on either "/" or "."
        assert len(idlist) in (3, 4)
        assert len(idlist[2]) <= 6
        idlist[2] = f'{int(idlist[2])}'
        if len(idlist) == 4:
            assert len(idlist[3]) <= 6
            idlist[3] = f'{int(idlist[3])}'
        return '.'.join(idlist)
    # Not an LDHRM/.. id
    m = re.match(r'(\D+)(\d+)([A-Za-z]?)(\.(\d+))?$', objid)
    # m = re.match(r'(\D+)(\d+)(.*)', objid)
    if m:
        if objid.startswith('JB'):  # pad with leading zeroes to 3 columns
            newobjid = m.group(1) + f'{int(m.group(2)):03d}' + m.group(3)
        else:
            newobjid = m.group(1) + f'{int(m.group(2))}' + m.group(3)
        if m.group(5):
            # denormalize sub-number
            newobjid += '.' + f'{int(m.group(5))}'
        return newobjid
    elif objid.isnumeric():
        return objid.lstrip('0')
    else:
        return objid


def sphinxify(txt: str, calledfromsphinx: bool) -> str:
    """ Sphinx displays '--' as '—' so partially work around that. """
    if not calledfromsphinx:
        return txt
    txt = re.sub(r'(--\w+)', r'``\1``', txt)
    return txt


if __name__ == '__main__':
    print('This module is not callable. Try src/normalize_xml.py')
