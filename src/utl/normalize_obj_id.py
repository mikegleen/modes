# -*- coding: utf-8 -*-
"""
The parameter is a string in the format of one of the types of object
identifiers in our Modes file.

Return a string normalized for sorting.

Input can be of the form JB001 or JB0001 or JB001a or SH1 or LDHRM/2018/1.
"""
import re


def normalize(objid):
    objid = objid.upper()
    if objid.startswith('LDHRM'):
        idlist = objid.split('/')
        assert len(idlist) == 3
        idlist[2] = f'{int(idlist[2]):0>4d}'
        return '/'.join(idlist)
    # Not an LDHRM/.. id
    m = re.match(r'(\D*)(\d*)(.*)', objid)
    if m:
        return m.group(1) + f'{int(m.group(2)):0>4d}' + m.group(3)
    else:
        raise ValueError(f'Bad format objid: {objid}')
