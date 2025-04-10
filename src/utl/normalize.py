# -*- coding: utf-8 -*-
"""
    Convert a datetime or date object to Modes format d[d].m[m].yyyy.
"""
import datetime
import re

DEFAULT_MDA_CODE = 'LDHRM'  # must be upper case
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
        d = datetime.datetime.strptime(indate, '%d.%m.%Y')
        nparts = 3
    except ValueError:
        try:
            d = datetime.datetime.strptime(indate, '%m.%Y')
            nparts = 2
        except ValueError:
            d = datetime.datetime.strptime(indate, '%Y')
            nparts = 1
    return d.date(), nparts


def datefrombritishdate(indate: str) -> tuple[datetime.date, int, str]:
    """
        Parse a string in Modes format (see datefrommodes) or
        a British date which can be:
            "d mmm yyyy"
            or "d month yyyy"
            or "mmm yyyy"
            or "month yyyy"
            or "dd/mm/yyyy"
            or "yyyy-mm-dd" (ISO 8601)
            It can also be yyyy but this is treated as Modes format.
        If day or month aren't given, the default values are returned.
    :param indate:
    :return: A tuple containing datetime.date and a part count followed by a
             date type indicator if a valid date exists otherwise an exception
             is raised.
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
    try:  # ISO 8601
        d = datetime.datetime.strptime(indate, "%Y-%m-%d").date()
        return d, 3, BRITISHTYPE
    except ValueError:
        pass
    try:  # 3 Mar 1917
        d = datetime.datetime.strptime(indate, '%d %b %Y').date()
        return d, 3, BRITISHTYPE
    except ValueError:
        pass
    try:  # 13/5/1917
        d = datetime.datetime.strptime(indate, '%d/%m/%Y').date()
        return d, 3, BRITISHTYPE
    except ValueError:
        pass
    try:  # 3 March 1917
        d = datetime.datetime.strptime(indate, '%d %B %Y').date()
        return d, 3, BRITISHTYPE
    except ValueError:
        pass
    try:  # Mar 1917
        d = datetime.datetime.strptime(indate, '%b %Y').date()
        return d, 2, BRITISHTYPE
    except ValueError:
        pass
    try:  # March 1917
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


def split_subid(objid: str, mdacode=DEFAULT_MDA_CODE) -> (str, int | None):
    """

    :param objid: A normalized or unnormalized accession number
                  like LDHRM.2018.22[.1] or JB001[.1]
    :param mdacode:
    :return: a tuple of the mainid and the subid if it exists or None. In the
             above example, mainid is 'LDHRM.2018.22' and subid is int(1).
    """
    len_with_sub = 4 if objid.startswith(mdacode) else 2
    parts = objid.split('.')
    if len(parts) == len_with_sub:
        mainid = '.'.join(parts[:-1])
        return mainid, int(parts[len_with_sub - 1])
    else:
        return objid, None


def is_subid(objid: str, mdacode=DEFAULT_MDA_CODE) -> bool:
    """
    :param objid: like JB001 or JB001.1 or LDHRM.2022.1 or LDHRM.2022.1.1
                    may be normalized
    :param mdacode: default like LDHRM
    :return: true if the objid is a subid
    """

    nobjid = normalize_id(objid, mdacode)
    return len(nobjid.split('.')) > 2 + nobjid.startswith(mdacode)


def normalize_id(objid, mdacode=DEFAULT_MDA_CODE, verbose=1, strict=True):
    """
    The parameter is a string in the format of one of the types of object
    identifiers (i.e. accession numbers) in our Modes file.

    Return a string normalized for sorting.
    Raises ValueError if the input is invalid.

    If a field that is expected to be an integer is not, a ValueError is
    raised or if strict == False, return the input object ID.

    strict=False is used in preview_dir.py where some of the files can have
    non-cannonical filenames but the order is only helpful, not necessary.

    Input can be of the form JB001 or JB0001 or JB001a or SH1 or with a leading
    MDA code: LDHRM/2018/1 or LDHRM.2018.1. or LDHRM.2018.1.2. If the leading
    "LDHRM." is omitted from an ID so that the first character is numeric, the "LDHRM."
    will be prepended. The "/" character is allowed as an alternative because
    some input files contain these. It is never used in the Modes data.
    Also allowed is LDHRM:2018.1 in the input data.

    For IDs with the MDA code, the one or two trailing numbers are expanded to
    six digits with leading zeroes if necessary. If an id contains a larger
    number an exception is raised. As a special case, JB numbers have a
    minimum of three digits which are expanded to six.
    For example:
    LDHRM.2018.1 -> LDHRM.2018.000001
    LDHRM.2018.1.2 -> LDHRM.2018.000001.000002
    JB001 -> JB000001
    JB001a -> JB000001A
    L001 -> L000001  # long term loan objects

    For IDs that are simple integers, these are expanded to eight digits.
    """
    if objid is None or len(objid) == 0:
        if strict:
            return None
        else:
            return ""
    objidu = objid.upper()
    if objidu[0].isnumeric():
        objidu = mdacode + '.' + objidu
    if objidu.startswith(mdacode):
        objidu = objidu.replace(':', '.', 1)  # accept LDHRM:...
        idlist = re.split(r'[/.]', objidu)  # split on either "/" or "."
        if len(idlist) not in (3, 4):
            raise ValueError(f'Bad accession ID, wrong number of fields: {objid}')
        if len(idlist[2]) > 6:
            raise ValueError(f'Third field, {idlist[2]}, of {objid} is too long')
        idlist[2] = f'{int(idlist[2]):06d}'
        if len(idlist) == 4:
            if len(idlist[3]) > 6:
                raise ValueError('Fourth field, {idlist[3]}, of {objid} is too long')
            idlist[3] = f'{int(idlist[3]):06d}'
        newobjid = '.'.join(idlist)
        if verbose > 3:
            print(f'normalize: {objid} -> {newobjid}')
        return newobjid

    # Not an LDHRM... id

    m = re.match(r'(\D+)(\d+)([A-Za-z]?)(\.(\d+))?$', objidu)
    # On a successful match, this patten returns five groups. If there is
    # no subgroup ID, groups 4 and 5 will be None. We are not interested in
    # group 4 as it includes the '.' followed by the subgroup ID whereas group
    # 5 includes just the subgroup ID. So:
    # JB123 -> ('JB', '123', '', None, None)
    # JB123A -> ('JB', '123', 'A', None, None)
    # JB123.2 -> ('JB', '123', '', '.2', '2')
    if m:
        if len(m.group(2)) > 6:
            raise ValueError(f'Length of field 2 > 6: "{objidu}"')
        newobjid = m.group(1) + f'{int(m.group(2)):06d}' + m.group(3)
        # See if it has a sub-number, like JB124.23
        if m.group(5):
            if len(m.group(5)) > 6:
                raise ValueError('Length of field 5 > 6: "{objidu}"')
            newobjid += '.' + f'{int(m.group(5)):06d}'
        if verbose > 3:
            print(f'normalize: {objid} -> {newobjid}')
        return newobjid
    if strict:
        raise ValueError(f'Unsupported accession ID format: "{objid}". Select'
                         f' option --allow_blank to continue.')
    else:
        print(f'normalize_id: Warning: unsupported accession ID format: "{objid}"')

    return objidu


def denormalize_id(objid: str, mdacode=DEFAULT_MDA_CODE):
    """
    :param objid: A normalized accession number
    :param mdacode: Default: LDHRM
    :return: An accession number with leading zeroes removed from numeric
             fields.
    """
    if objid.startswith(mdacode):
        idlist = objid.split('.')
        assert len(idlist) in (3, 4)
        assert len(idlist[2]) <= 6
        idlist[2] = f'{int(idlist[2])}'  # remove leading zeroes
        if len(idlist) == 4:
            assert len(idlist[3]) <= 6
            idlist[3] = f'{int(idlist[3])}'  # remove leading zeroes
        return '.'.join(idlist)
    # Not an LDHRM/.. id
    # The following regex matches (by group):
    # 1. 'JB' or 'L'
    # 2. nnnnnn - number padded to 6 digits
    # 3. optional trailing letter
    # 4. .nnnnnn - item number with leading period
    # 5. nnnnnn - same as group 4 without leading period
    m = re.match(r'(\D+)(\d+)([A-Za-z]?)(\.(\d+))?$', objid)
    if m:
        if m[1].upper() in ('JB', 'L'):
            # pad with leading zeroes to 3 columns
            newobjid = m[1] + f'{int(m[2]):03d}' + m[3]
        else:
            newobjid = m[1] + f'{int(m[2])}' + m[3]
        if m.group(5):
            # denormalize sub-number
            newobjid += '.' + f'{int(m[5])}'
        return newobjid
    else:
        fields = objid.split('.')
        return '.'.join([field.lstrip('0') for field in fields])


def if_not_sphinx(txt: str, calledfromsphinx: bool) -> str:
    """ For example, Sphinx automatically displays the default value
        so don't display it in the text.
    """
    if not calledfromsphinx:
        return txt
    return ''


def sphinxify(txt: str, calledfromsphinx: bool) -> str:
    """ Sphinx displays '--' as  an em dash, '—', so partially work around
    that. """
    if not calledfromsphinx:
        return txt
    # print(f'before:{txt}')
    txt = re.sub(r'(--\w+)', r'``\1``', txt)
    # print(f'after:{txt}')
    return txt


def modes_person(person: str) -> str:
    """

    :param person: A name in the form of <given-name(s)> <family-name> or
                   <family-name>, <given-name(s)>
    :return: The name in format <family-name>, <given-name(s)>
    """
    if ',' in person:
        return person
    parts = person.split()
    if len(parts) <= 1:
        return person
    fullname = f'{parts[-1]}, {" ".join(parts[:-1])}'
    return fullname


if __name__ == '__main__':
    print('This module is not callable. Try src/normalize_xml.py')
