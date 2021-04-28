"""
    Convert References/Reference/Date elements from 17 May 1909 to 17.5.1919
"""
import argparse
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
import resource
import sys

from utl.cfgutil import Stmt
from utl.normalize import modesdate, datefrombritishdate, MODESTYPE


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_object(objelt: ET.Element, idnum: str) -> bool:
    """
    :param objelt: the Object
    :param idnum: the ObjectIdentity/Number text (for trace)

    :return: True if an object is updated
    """
    references = objelt.findall('./References/Reference')
    updated = False
    for reference in references:
        refdate = reference.find('./Date')
        if refdate is None:
            continue
        refdatetext: str = refdate.text
        if refdatetext is None or len(refdatetext) == 0:
            continue
        try:
            newdate, partcount, datetype = datefrombritishdate(refdatetext)
        except ValueError:
            continue
        if datetype == MODESTYPE:  # if it's already a Modes format date
            continue
        mdate = modesdate(newdate, partcount)
        refdate.text = mdate
        updated = True
        trace(2, '{}: {} -> {}', idnum, refdatetext, mdate)
    return updated


def main():
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    written = 0
    numupdated = 0
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find(Stmt.get_default_record_id_xpath())
        idnum = idelem.text if idelem is not None else None
        trace(3, 'idnum: {}', idnum)
        updated: bool = one_object(elem, idnum)
        numupdated += 1 if updated else 0
        if updated or _args.all:
            outfile.write(ET.tostring(elem, encoding='utf-8'))
            written += 1
        elem.clear()
        if updated and _args.short:
            break
    outfile.write(b'</Interchange>')
    print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    trace(1, f'End reference_date.py. {written} object'
             f'{"s" if written != 1 else ""} written '
             f'of which {numupdated} updated.')


def getargs():
    parser = argparse.ArgumentParser(description='''
    Convert References/Reference/Date elements from 17 May 1909 to 17.5.1919
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects. The default is to only write updated objects.''')
    parser.add_argument('--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}', _args.infile)
    trace(1, 'Creating file: {}', _args.outfile)
    main()
