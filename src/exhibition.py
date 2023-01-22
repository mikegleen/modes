"""
    Import exhibition information into a Modes XML file.

    Input: - exhibition list maintained in src/cfg/exhibition_list.py
           - input XML file.
           - CSV file of objects in an exhibition. CSV format:
               accession#,[exhibition#],[catalogue#]
           The exhibition # is optional and is ignored if the --exhibition
           parameter is given. The accession number may contain a string
           specifying multiple numbers of the form JB001-003.
           The catalogue number is optional and is set if specified. The
           columns numbers may be specified by progrm arguments; The accession
           number and exhibition number default to columns zero and one
           respectively and the catalogue # is only processed if the argument
           is specified.
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
from utl.cfgutil import Stmt, expand_idnum
from utl.excel_cols import col2num
from utl.normalize import modesdate, normalize_id, denormalize_id, datefrommodes
from utl.normalize import sphinxify, vdate

ExhibitionTuple = namedtuple('ExhibitionTuple',
                             'ExNum DateBegin DateEnd ExhibitionName Place')


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_object(objelt, idnum, exhibition: ExhibitionTuple, catalog_num=''):
    """
#
    :param objelt: the Object
    :param idnum: the ObjectIdentity/Number text (for trace)
    :param exhibition: the Exhibition tuple corresponding to exhibition_list.py
    :param catalog_num: for the CatalogueNumber element
    :return: a tuple containing the BeginDate, the new Exhibition element
    """
    global found_old_key

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

        It is possible to have duplicate exhibition names but exhibitions are
        guaranteed to have unique name+place+begindate. So if we are replacing
        the name, make sure that we are updating the correct exhibition by
        checking the complete keys.
        """

        exhibname = exhib_elt.find('ExhibitionName')
        if exhibname is None:
            return 0  # This is an empty Exhibition template
        # Updating the exhibition name is a special case since it's used as
        # a key.  The old name is in the XML file and is to be replaced. We
        # could skip this step as the full key compare will work anyhow, but
        # this gets us out of here quickly in most cases.
        if exhibname.text not in (_oldname, exhibition.ExhibitionName):
            return 1  # not a match so just keep this element as is
        # The exhibition names match but if they are duplicated elsewhere in
        # the list, we must look deeper.
        exhibkey = _oldname if _oldname else exhibition.ExhibitionName + ':'
        exhibkey += _oldplace if _oldplace else exhibition.Place + ':'
        exhibkey += _olddate if _olddate else (exhibition.DateBegin.isoformat()[:10])
        xmlkey = exhibname.text
        xmlplace = ''
        xmldate = ''
        subelts = list(exhib_elt)
        for subelt in subelts:
            tag = subelt.tag
            if tag == "Place":
                xmlplace = subelt.text
            elif tag == "Date":
                dates = list(subelt)
                for dateelt in dates:
                    if dateelt.tag == 'DateBegin':
                        xmldate = dateelt.text
                        break
        xmlkey += ':' + xmlplace + ':' + xmldate
        # And finally, confirm that it's really the one we want to update.
        trace(3, '{}: exhibkey={}\nxmlkey={}', idnum, exhibkey, xmlkey)
        if exhibkey != xmlkey:
            return 1
        # The names match so update the values
        for subelt in subelts:
            tag = subelt.tag
            if tag == "ExhibitionName":
                subelt.text = exhibition.ExhibitionName
            elif tag == "CatalogueNumber":
                subelt.text = str(catalog_num)
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
                      ' element not updated.', subelt.text, display_id, tag)
        return 2
    # end one_exhibition

    display_id = denormalize_id(idnum)
    trace(3, 'one_object: {} {}', display_id, exhibition)
    elts = list(objelt)  # the children of Object
    # for elt in elts:
    #     print(elt)
    exhibs_to_insert = list()  # all current plus any new
    exhibs_to_remove = list()  # empty Exhibition template or to be deleted
    firstexix = None  # index of the first Exhibition element
    need_new = True
    for n, elt in enumerate(elts):
        if elt.tag == "Exhibition":
            if firstexix is None:
                firstexix = n
            status = one_exhibition(elt)
            if status == 0:  # This is an empty Exhibition template
                exhibs_to_remove.append(elt)
                continue
            begindate, _ = datefrommodes(elt.find('./Date/DateBegin').text)
            if status == 1:  # Not this exhibition
                # The <Exhibition> element from the XML file is not one we're
                # interested in so just put it on the list to be written out.
                trace(2, f'Keeping {display_id}')
                exhibs_to_insert.append((begindate, elt))  # will sort on date
                continue
            else:  # status == 2
                # Sanity check that we got at least one hit on the --old_xxxx parameter
                found_old_key = True
                need_new = False
                if _args.delete:
                    trace(2, f'Removing {display_id}')
                    exhibs_to_remove.append(elt)
                else:
                    trace(2, f'Updating {display_id}')
                    exhibs_to_insert.append((begindate, elt))  # will sort on date
    if firstexix is None:  # no Exhibition elements were found
        etype = objelt.get('elementtype')
        trace(1, '{}: No Exhibition element. etype: “{}”. '
                 'Inserting the new exhibition after the Acquisition element.',
              display_id, etype)
        for n, elt in enumerate(elts):
            if elt.tag == "Acquisition":
                firstexix = n + 1  # insert the new elt after <Acquisition>
                break
    # Remove all the Exhibition elements and re-insert the ones we're
    # keeping in date order.
    for _edate, exhib in exhibs_to_insert:
        # print(objelt, exhib)
        objelt.remove(exhib)
    for exhib in exhibs_to_remove:
        objelt.remove(exhib)
    if need_new:
        newexhibit = new_exhib()  # returns a tuple of (date, element)
        trace(2, f'Adding {display_id}')
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
    exhibition_list = EXSTR.split('\n')
    reader = csv.reader(exhibition_list, delimiter=',')
    next(reader)  # skip heading

    exdic = {}
    for row in reader:
        if not row:
            continue
        exdic[int(row[0])] = ExhibitionTuple(ExNum=row[0],
                                             DateBegin=date.fromisoformat(row[1]),
                                             DateEnd=date.fromisoformat(row[2]),
                                             ExhibitionName=row[3],
                                             Place=row[4] if len(row) >= 5 else 'HRM'
                                             )
        if exdic[int(row[0])].DateBegin > exdic[int(row[0])].DateEnd:
            raise ValueError(f"In exhibition_list.py, Begin Date > End Date: {row}")
    if _args.exhibition:
        exnum = _args.exhibition
        trace(1, 'Processing exhibition {}: "{}"', exnum,
              exdic[exnum].ExhibitionName)
    return exdic


def get_csv_dict(csvfile):
    """
    :param: csvfile: contains the accession number specified by --col_acc,
    optionally the exhibition number in the column specified by  and --col_ex,
    and optionally the catalog number specified by --col_cat.
    :return: A dict with the key of the accession number and the value being
             a tuple of (exhibition number, catalogue number).
    """
    def one_accession_number(accno):
        # print(f'{row=}')
        try:
            accnum = normalize_id(accno)
        except ValueError:
            print(f"Skipping badly formed accession # in csv: {accno}")
            return
        if accnum in cdict:
            raise KeyError(f'Duplicate accession number: {accnum}')
        cataloguenumber = None
        if _args.col_cat is not None:
            cataloguenumber = row[_args.col_cat]
            try:
                # convert "33." to 33
                cataloguenumber = int(float(cataloguenumber))
            except ValueError:
                pass  # ok, doesn't have to be an integer
        # print(row)
        # print(exhibition, cataloguenumber)
        cdict[accnum] = (exhibition, cataloguenumber)

    with codecs.open(csvfile, 'r', 'utf-8-sig') as mapfile:
        cdict = {}
        reader = csv.reader(mapfile)
        for n in range(_args.skiprows):
            next(reader)
        for row in reader:
            accnumber = row[_args.col_acc]
            if not accnumber:
                continue  # blank accession number
            if _args.exhibition:
                exhibition = _args.exhibition
            else:
                col_ex = _args.col_ex
                try:
                    exhibition = int(row[col_ex])
                except (IndexError, ValueError) as e:
                    if _args.allow_missing:
                        trace(2, 'Missing exhibition number, skipping {}',
                              accnumber)
                        continue
                    print(f'Missing column {col_ex}, accession #: {accnumber}')
                    raise e
            # The "accnumber" might actually be a range of accession numbers
            # in the form JB001-002:
            accnumlist = expand_idnum(accnumber)
            for accn in accnumlist:
                one_accession_number(accn)
    trace(3, 'get_csv_dict: {}', cdict)
    return cdict


def main():
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    if _args.object:
        objlist = expand_idnum(_args.object)  # JB001-002 -> JB001, JB002
        exmap = {normalize_id(obj):  # JB001 -> JB00000001
                 (_args.exhibition, _args.catalogue) for obj in objlist}
    else:
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
        trace(1, 'In CSV but not XML: "{}"', denormalize_id(idnum))
    trace(1, f'End exhibition.py. {written} object'
             f'{"s" if written != 1 else ""} written '
             f'of which {numupdated} updated.')


def getparser():
    parser = argparse.ArgumentParser(description=sphinxify('''
        Import exhibition information into a Modes XML file.
        Read a CSV file using the --mapfile argument containing one, two, or
        three columns containing 
        the accession number whose record should be updated, the
        optional exhibition number, and the optional catalogue number. The
        exhibition number corresponds to the data in exhibition_list.py and
        is used for this process but is not recorded in the XML file.
        
        Instead
        of including the exhibition number in the CSV file, you can specify
        a single exhibition number to apply to all rows using  the --exhibition
        argument. If you need to process a single object, you can omit the
        --mapfile argument and specify a single object wth the --object
        argument. See also the --catalogue argument.
        ''', called_from_sphinx))
    exgroup = parser.add_mutually_exclusive_group()
    objgroup = parser.add_mutually_exclusive_group()
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects. The default is to only write updated objects.''')
    parser.add_argument('--allow_missing', action='store_true', help='''
        Skip rows with missing exhibition numbers. Otherwise abort.''')
    parser.add_argument('--col_acc', help='''
        The zero-based column containing the accession number of the
        object to be updated. The default is column zero. The column can be a
        number or a spreadsheet-style letter.''')
    parser.add_argument('-c', '--catalogue', help='''
        The catalogue number. Only specify this if a single object is specified
        with the -j option.
        ''')
    parser.add_argument('--col_cat', help='''
        The zero-based column containing the catalog number of the
        object in the corresponding exhibition. The default is to not create
        a catalog number sub-element. The column can be a number or a
        spreadsheet-style letter.''')
    exgroup.add_argument('--col_ex', help=sphinxify('''
        The zero-based column containing the exhibition number.
        Do not specify this if --exhibition is specified. It is mandatory
        otherwise. The column can be a number or a spreadsheet-style
        letter.''', called_from_sphinx))
    parser.add_argument('--delete', action='store_true', help=sphinxify('''
        Delete this exhibition from all objects selected.
        Requires --exhibition.''', called_from_sphinx))
    exgroup.add_argument('-e', '--exhibition', type=int, help=sphinxify('''
        The exhibition number
        to apply to all objects in the CSV file. Do not specify this if
        --col_ex is specified.''', called_from_sphinx))
    objgroup.add_argument('-m', '--mapfile', help=sphinxify('''
        The CSV file mapping the accession number to the catalog number and
        exhibition number. (but see --exhibition). There is no heading row
        (but see --skiprows).''', called_from_sphinx))
    objgroup.add_argument('-j', '--object', help=sphinxify('''
    Specify a single object to be processed. If specified, do not specify
    the CSV file containing object numbers, exhibitions and catalogue numbers
    (--mapfile). You must also specify --exhibition and optionally --catalogue.
    ''', called_from_sphinx))
    parser.add_argument('--old_name', help=sphinxify('''
    Specify the old name of the exhibition to be replaced by the name now in
    ``exhibition_list.py``. You must specify the --exhibition parameter.
        ''', called_from_sphinx))
    parser.add_argument('--old_place', help=sphinxify('''
    Specify the old ``Place`` of the exhibition to be replaced by the ``Place``
    now in ``exhibition_list.py``. You must specify the --old_name parameter.
    This is optional and only needed if the exhibition name is not unique.
        ''', called_from_sphinx))
    parser.add_argument('--old_date', help=sphinxify('''
    Specify the old BeginDate of the exhibition to be replaced by the BeginDate
    now in ``exhibition_list.py``. This is optional and only needed if the
    exhibition name is not unique. You must specify the --old_place parameter.
    The date must be in Modes format (d.m.yyyy).
        ''', called_from_sphinx))
    parser.add_argument('-s', '--skiprows', type=int, default=0, help='''
        Number of lines to skip at the start of the CSV file''')
    parser.add_argument('--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if args.mapfile is None and args.object is None:
        raise ValueError('You must specify one of --mapfile and --object')
    if (args.object or args.old_name) and not args.exhibition:
        raise(ValueError('You specified the object id or old name. You must'
                         ' also specify the exhibition.'))
    if args.delete and not args.exhibition:  # Modes format?
        raise ValueError('You specified --delete. You must also specify the'
                         ' exhibition.')
    if args.col_acc is None:
        args.col_acc = 0
    else:
        args.col_acc = col2num(str(args.col_acc))
    if args.col_cat is not None:
        args.col_cat = col2num(str(args.col_cat))
    if args.col_ex is not None:
        args.col_ex = col2num(str(args.col_ex))

    if args.old_date:
        if not vdate(args.old_date):  # Modes format?
            raise ValueError('Parameter --old_date must be Modes format, d.m.yyyy')

    return args


called_from_sphinx = True


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    called_from_sphinx = False
    found_old_key = False
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    _oldname = _args.old_name
    _oldplace = _args.old_place
    _olddate = _args.old_date
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}', _args.infile)
    trace(1, 'Creating file: {}', _args.outfile)
    main()
    if (_oldname or _oldplace or _olddate) and not found_old_key:
        print("**** Warning: Old name/place/date specified but no old key found.")
