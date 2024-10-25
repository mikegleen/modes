
import re
COLLECTION_PREFIX = 'collection_'

#
#   <accession #>-<3-digit subnumber>[<A|B>][-<page #>][<A|B>]
#   The 'A|B' can either follow the subnumber or the page number (or neither)
#   but not both. This is not enforced by the pattern.
#
FILENAMEPAT = (r'^(?P<accn>[^\-]*)'
               r'(-((?P<subn>\d{3})(?P<subnAB>[A-Z])?(-(?P<page>\d+)(?P<pageAB>[A-Z])?)?))?')
#                1 23             33               3 3 4           44               4 3 21

#
# FILENAMEPAT2 is for the case where there is "--" in the filename indicating
# that this is an accession number without subnumbers but with page numbers.
#
FILENAMEPAT2 = (r'^(?P<accn>[^\-]*)'
                r'--((?P<page>\d+)(?P<pageAB>[A-Z])?)')
#                   12           22               2 1


def parse_prefix(prefix):
    """

    :param prefix: Part of the filename except the trailing extension (such
                   as '.jpg')
    :return: a tuple of parts, for example:

        'JB001-001-3A'
    returns:
        accn:    'JB001'
        subn:    '001'
        subn_ab: ''
        page:    '3'
        page_ab: 'A'
        modes_key1: 'JB001'
        modes_key2: 'JB001.1' or None


    """
    prefix = prefix.removeprefix(COLLECTION_PREFIX)
    if '--' in prefix:
        # There is no subnum but there is a page number.
        m = re.match(FILENAMEPAT2, prefix)
        if not m:
            raise ValueError(f'File prefix failed match (FILENAMEPAT2): {prefix}')
        accn = m['accn']
        subn = subn_ab = ''
        page = m['page']
        page_ab = m['pageAB'] if m['pageAB'] else ''
        modes_key1 = accn
        modes_key2 = None
    else:
        m = re.match(FILENAMEPAT, prefix)
        if not m:
            raise ValueError(f'File prefix failed match (FILENAMEPAT): {prefix}')
        accn = m['accn']
        modes_key1 = accn
        if m['subn']:
            subn = m["subn"]
            subn_ab = m['subnAB'] if m['subnAB'] else ''
            modes_key2 = f'{accn}.{int(subn)}'
            page = m['page'] if m['page'] else ''
            page_ab = m['pageAB'] if m['pageAB'] else ''
        else:
            subn = subn_ab = page = page_ab = ''
            modes_key2 = None
    return accn, subn, subn_ab, page, page_ab, modes_key1, modes_key2
