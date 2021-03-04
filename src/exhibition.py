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
            <CatalogueNumber />
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
from datetime import date
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from cfg.exhibition_list import EXSTR
from utl.cfgutil import Stmt
from utl.normalize import modesdate, normalize_id, denormalize_id, datefrommodes

Exhibition = namedtuple('Exhibition',
                        'ExNum DateBegin DateEnd ExhibitionName Place')


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_object(objelt, idnum, exhibition: Exhibition, catalog_num=None):
    """

    :param objelt: the Object
    :param idnum: the ObjectIdentity/Number text (for trace)
    :param exhibition: the Exhibition tuple corresponding to exhibition_list.py
    :param catalog_num: for the CatalogueNumber element
    :return: a tuple containing the BeginDate, the new Exhibition element
    """
    def new_exhib():
        newelt = ET.Element('Exhibition')
        subelt = ET.SubElement(newelt, 'ExhibitionName')
        subelt.text = exhibition.ExhibitionName
        if catalog_num is not None:
            subelt = ET.SubElement(newelt, 'CatalogueNumber')
            subelt.text = str(catalog_num)
        subelt = ET.SubElement(newelt, 'Place')
        subelt.text = exhibition.Place
        dateelt = ET.SubElement(newelt, 'Date')
        subelt = ET.SubElement(dateelt, 'DateBegin')
        subelt.text = modesdate(exhibition.DateBegin)
        subelt = ET.SubElement(dateelt, 'DateEnd')
        subelt.text = modesdate(exhibition.DateEnd)
        return exhibition.DateBegin, newelt

    def one_exhibition(exhib_elt):
        """
        Handle an existing exhibition
        :param exhib_elt: an Exhibition element (under Object)
        :return: 0 if it is an empty template
                 1 if the input element's ExhibitionName is different from
                    the one we are inserting
                 2 (also update the values) if the ExhibitionName values match
        """
        exhname = exhib_elt.find('ExhibitionName')
        if exhname is None:
            return 0  # This is an empty Exhibition template
        if exhname.text != exhibition.ExhibitionName:
            return 1  # not a match so just keep this element as is
        # The names match so update the values
        subelts = list(exhib_elt)
        for subelt in subelts:
            tag = subelt.tag
            if tag == "ExhibitionName":
                subelt.text = exhibition.ExhibitionName
            elif tag == "Place":
                subelt.text = exhibition.Place
            elif tag == "Date":
                dates = list(subelt)
                for dateelt in dates:
                    if dateelt.tag == 'DateBegin':
                        dateelt.text = modesdate(exhibition.DateBegin)
                    elif dateelt.tag == 'DateEnd':
                        dateelt.text = modesdate(exhibition.DateEnd)
            else:
                trace(1, 'ID {}: Unknown subelt in {} Exhibition element: {},' 
                      ' element not updated.', display_id, tag)
        return 2
    # end one_exhibition

    display_id = denormalize_id(idnum)
    trace(2, 'one_element: {} {}', display_id, exhibition)
    elts = list(objelt)  # the children of Object
    # for elt in elts:
    #     print(elt)
    exhibs_to_insert = list()
    exhibs_to_remove = list()
    firstexix = None  # index of the first Exhibition element
    need_new = True
    for n, elt in enumerate(elts):
        if elt.tag == "Exhibition":
            status = one_exhibition(elt)
            if status:  # 1 or 2
                # Assume DateBegin exists
                begindate = datefrommodes(elt.find('./Date/DateBegin').text)
                exhibs_to_insert.append((begindate, elt))
                if status == 2:
                    need_new = False
            else:
                exhibs_to_remove.append(elt)  # empty template
            if firstexix is None:
                firstexix = n
    if firstexix is None:  # no Exhibition elements were found
        etype = objelt.get('elementtype')
        trace(1, 'Object number {}: No Exhibition element. etype: {}',
              idnum, etype)
        for n, elt in enumerate(elts):
            if elt.tag == "Acquisition":
                firstexix = n + 1  # insert the new elt after <Acquisition>
                break
    for _edate, exhib in exhibs_to_insert:
        # print(objelt, exhib)
        objelt.remove(exhib)
    for exhib in exhibs_to_remove:
        objelt.remove(exhib)
    if need_new:
        newexhibit = new_exhib()  # returns a tuple of (date, element)
        exhibs_to_insert.append(newexhibit)
    # Insert the Exhibition elements with the most recent one first
    for _edate, exhib in sorted(exhibs_to_insert):
        objelt.insert(firstexix, exhib)


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
                        DateBegin=date.fromisoformat(row[1]),
                        DateEnd=date.fromisoformat(row[2]),
                        ExhibitionName=row[3],
                        Place=row[4] if len(row) >= 5 else 'HRM'
                        ) for row in reader}
    if _args.exhibition:
        exnum = _args.exhibition
        trace(1, 'Processing exhibition {}: "{}"', exnum,
              exdic[exnum].ExhibitionName)
    return exdic


def get_csv_dict(csvfile):
    """
    :param csvfile: contains the accession number specified by --col_acc,
    optionally the exhibition number in the column specified by  and --col_ex,
    and optionally the catalog number specified by --col_cat.
    :return: A dict with the key of the accession number and the value being
             the exhibition number.
    """
    with codecs.open(csvfile, 'r', 'utf-8-sig') as mapfile:
        cdict = {}
        reader = csv.reader(mapfile)
        for n in range(_args.skiprows):
            next(reader)
        for row in reader:
            accnum = row[_args.col_acc]
            if not accnum:
                continue  # blank accession number
            try:
                accnum = normalize_id(accnum)
            except ValueError:
                print(f"Skipping in csv: {accnum}")
                continue
            if _args.exhibition:
                exhibition = _args.exhibition
            else:
                col_ex = _args.col_ex
                try:
                    exhibition = int(row[col_ex])
                except IndexError as e:
                    print(f'Missing column {col_ex}, accession #: {accnum}')
                    raise e
            if accnum in cdict:
                raise ValueError(f'Duplicate accession number: {accnum}')
            cataloguenumber = None
            if _args.col_cat is not None:
                cataloguenumber = row[_args.col_cat]
            # print(row)
            # print(exhibition, cataloguenumber)
            cdict[accnum] = (exhibition, cataloguenumber)
    trace(2, 'get_csv_dict: {}', cdict)
    return cdict


def main():
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    exmap = get_csv_dict(_args.mapfile)  # acc # -> (exhibition #, catalog #)
    exdict = get_exhibition_dict()  # exhibition # -> Exhibition tuple
    written = 0
    numupdated = 0
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find(Stmt.get_default_record_id_xpath())
        idnum = idelem.text if idelem is not None else None
        idnum = normalize_id(idnum)
        trace(3, 'idnum: {}', idnum)
        if idnum and idnum in exmap:
            exnum, cataloguenumber = exmap[idnum]
            one_object(elem, idnum, exdict[exnum], cataloguenumber)
            del exmap[idnum]
            updated = True
            numupdated += 1
        else:
            updated = False
        if updated or _args.all:
            outfile.write(ET.tostring(elem, encoding='utf-8'))
            written += 1
        if updated and _args.short:
            break
    outfile.write(b'</Interchange>')
    for idnum in exmap:
        trace(1, 'In CSV but not XML: "{}"', idnum)
    trace(1, f'End exhibition.py. {written} object'
             f'{"s" if written != 1 else ""} written '
             f'of which {numupdated} updated.')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Import exhibition information into a Modes XML file.
        Read a CSV file containing one or two columns. The first column is
        the accession number whose record should be updated. The second
        column is the optional exhibition number.
        (see --exhibition for details).
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects. The default is to only write updated objects.''')
    parser.add_argument('--col_acc', default=0, type=int, help='''
        The zero-based column containing the accession number of the
        object to be updated. ''')
    parser.add_argument('--col_cat', type=int, help='''
        The zero-based column containing the catalog number of the
        object in the corresponding exhibition. ''')
    parser.add_argument('--col_ex', default=1, type=int, help='''
        The zero-based column containing the exhibition number.
        Ignored if --exhibition is specified. ''')
    parser.add_argument('-e', '--exhibition', type=int, help='''
        The exhibition number, corresponding to the data in exhibition_list.py
        to apply to all objects in the CSV file.''')
    parser.add_argument('-m', '--mapfile', required=True, help='''
        The CSV file mapping the object number to the exhibition number
        (but see --exhibition). There is no heading row.''')
    parser.add_argument('-s', '--skiprows', type=int, default=0, help='''
        Number of lines to skip at the start of the CSV file''')
    parser.add_argument('--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}', _args.infile)
    trace(1, 'Creating file: {}', _args.outfile)
    main()
