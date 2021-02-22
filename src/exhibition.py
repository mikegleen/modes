"""
    Import exhibition information into a Modes XML file.

    Input: exhibition list maintained in src/cfg/exhibition_list
           input XML file.
           CSV file of objects in an exhibition. CSV format:
               accession#,[exhibition#]
           The exhibition # is optional and is ignored if the --exhibition
           parameter is given.
    Output: updated XML file

    The Exhibition group template is:
        <Exhibition>
            <ExhibitionName />
            <Place />
            <Date>
                <DateBegin />
                <DateEnd />
            </Date>
        </Exhibition>
"""
import argparse
import codecs
from collections import namedtuple
import csv
from datetime import datetime
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from cfg.exhibition_list import EXSTR
from utl.cfgutil import Stmt
from utl.normalize import modesdate, normalize_id, denormalize_id

Exhibition = namedtuple('Exhibition',
                        'ExNum DateBegin DateEnd ExhibitionName Place')


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_element(elem, idnum, exhibition: Exhibition):
    """

    :param elem: the Object
    :param idnum: the ObjectIdentity/Number text (for trace)
    :param exhibition: the Exhibition tuple corresponding to exhibition_list.py
    :return: None. The exhibition is inserted into the Object element.
    """
    def new_exhib():
        newelt = ET.Element('Exhibition')
        subelt = ET.SubElement(newelt, 'ExhibitionName')
        subelt.text = exhibition.ExhibitionName
        subelt = ET.SubElement(newelt, 'Place')
        subelt.text = exhibition.Place
        dateelt = ET.SubElement(newelt, 'Date')
        subelt = ET.SubElement(dateelt, 'DateBegin')
        subelt.text = exhibition.DateBegin
        subelt = ET.SubElement(dateelt, 'DateEnd')
        subelt.text = exhibition.DateEnd
        return newelt
    trace(2, 'one_element: {} {}', denormalize_id(idnum), exhibition)
    elts = list(elem)  # the children of Object
    lastexix = None  # index of the last Exhibition element
    firstexix = None
    nexelts = 0  # number of Exhibition elements
    for n, elt in enumerate(elts):
        if elt.tag == "Exhibition":
            exname = elt.find('ExhibitionName')
            # print(f'{exname.text=}')
            # print(f'{exhibition.ExhibitionName=}')
            if exname is not None and exname.text == exhibition.ExhibitionName:
                trace(1, 'Object number {}: Replacing "{}"',
                      denormalize_id(idnum), exhibition.ExhibitionName)
                firstexix = n
                nexelts = -1  # bypass special cases below
                del elem[n]
                break
            elif firstexix is None:
                firstexix = n
            nexelts += 1
            lastexix = n
    if nexelts == 0:
        etype = elem.get('elementtype')
        trace(1, 'Object number {}: No Exhibition element. etype: {}',
              idnum, etype)
        for n, elt in enumerate(elts):
            if elt.tag == "Acquisition":
                firstexix = n + 1  # insert the new elt after <Acquisition>
                break
    elif nexelts == 1:
        exhib = elts[lastexix]
        ename = exhib.find('./ExhibitionName')
        if ename is None:
            # There is no exhibition name so this element is the empty one
            # from the template.
            # elem.remove(exhib)
            del elem[lastexix]
    # Insert the new Exhibition elment before the first existing one.
    exhib = new_exhib()
    elem.insert(firstexix, exhib)


def get_exhibition_dict():
    """
    EXSTR is imported from exhibition_list.py and contains a CSV formatted
    multi-line string. The heading line contains:
        ExNum,DateBegin,DateEnd,ExhibitionName[,Place]

    :return: A dictionary mapping the exhibition number to the Exhibition
             namedtuple.
    """
    reader = csv.reader(EXSTR.split('\n'), delimiter=',')
    next(reader)  # skip heading
    exdic = {int(row[0]):
             Exhibition(ExNum=row[0],
                        DateBegin=modesdate(datetime.strptime(row[1],
                                                              '%d/%m/%Y')),
                        DateEnd=modesdate(datetime.strptime(row[2],
                                                            '%d/%m/%Y')),
                        ExhibitionName=row[3],
                        Place=row[4] if len(row) >= 5 else 'HRM'
                        ) for row in reader}
    return exdic


def get_csv_dict(csvfile):
    """

    :param csvfile: contains the accession number and optionally the exhibition
                    number in columns specified by --serial and --ex_col
    :return: A dict with the key of the serial number and the value being
             the exhibition number.
    """
    with codecs.open(csvfile, 'r', 'utf-8-sig') as mapfile:
        cdict = {}
        reader = csv.reader(mapfile)
        for row in reader:
            serial = normalize_id(row[_args.serial])
            if _args.exhibition:
                exhibition = _args.exhibition
            else:
                ex_col = _args.ex_col
                try:
                    exhibition = int(row[ex_col])
                except IndexError as e:
                    print(f'Missing column {ex_col}, accession #: {serial}')
                    raise e
            cdict[serial] = exhibition
    trace(2, 'get_csv_dict: {}', cdict)
    return cdict


def main():
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    exmap = get_csv_dict(_args.mapfile)  # serial -> exhibition #
    exdict = get_exhibition_dict()  # exhibition # -> Exhibition tuple
    visited = set()
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find(Stmt.get_default_record_id_xpath())
        idnum = idelem.text if idelem is not None else None
        idnum = normalize_id(idnum)
        trace(3, 'idnum: {}', idnum)
        if idnum and idnum in exmap:
            if idnum in visited:
                raise ValueError(f'Duplicate accession number in CSV: {idnum}')
            exnum = exmap[idnum]
            one_element(elem, idnum, exdict[exnum])
            del exmap[idnum]
            visited.add(idnum)
            updated = True
        else:
            updated = False
        if updated or _args.all:
            outfile.write(ET.tostring(elem, encoding='utf-8'))
        if updated and _args.short:
            break
    outfile.write(b'</Interchange>')
    for idnum in exmap:
        trace(1, 'In CSV but not XML: "{}"', idnum)


def getargs():
    parser = argparse.ArgumentParser(description='''
        Import exhibition information into a Modes XML file.
        Read a CSV file containing one or two columns. The first column is
        the accession number whose record should be updated. The second
        column is the optional exhibition number
        (see --exhibition for details).
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects. The default is to only write updated objects.''')
    parser.add_argument('-e', '--exhibition', required=False,
                        type=int, help='''
        The exhibition number, corresponding to the data in exhibition_list.py
        to apply to all objects in the CSV file.''')
    parser.add_argument('--ex_col', default=1, type=int, help='''
        The zero-based column containing the exhibition number.
        Ignored if --exhibition is specified. ''')
    parser.add_argument('-m', '--mapfile', required=True, help='''
        The CSV file mapping the object number to the exhibition number
        (but see --exhibition). There is no heading row.''')
    parser.add_argument('--serial', required=False, default=0, type=int,
                        help='''
        The zero-based column number containing the accession number of the
        object to be updated. ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    # print(exdict)
    # sys.exit()
    _args = getargs()
    nupdated = nunchanged = 0
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}', _args.infile)
    trace(1, 'Creating file: {}', _args.outfile)
    main()
    # trace(1, 'End update_from_csv. {}/{} object{} updated. {} existing'
    #       ' element{} unchanged.', nupdated, nnewvals,
    #       '' if nupdated == 1 else 's', nunchanged,
    #       '' if nunchanged == 1 else 's')
