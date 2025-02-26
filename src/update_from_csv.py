# -*- coding: utf-8 -*-
"""

    The input is three files, an XML file, a YAML file and a CSV file. The
    XML file is the Modes database file to be updated. The YAML file
    contains definitions for elements to be updated from a CSV file.
    The format of the CSV file is that the first column contains a serial
    number and subsequent columns contain the values to be inserted into the
    corresponding elements. Note that there is no entry in the YAML file
    for the serial number column in the CSV file.

    The YAML file contains multiple documents, separated by lines containing
    "---"; each document corresponds to an element to be updated. The following
    example is of a single element to be updated::

        ---
        cmd: column
        xpath: ./ObjectLocation/Reason

    The documents may contain "title" statements.  If a title statement is
    not included a best-guess will be made from the final part of the **xpath**
    statement. In the above example, the column title in the CSV file is “Reason”.
    See the description of the **Title** statement in the configuration section.

    Subid Mode
    ----------

    Subid mode is selected by the presence of the **subid_parent** and
    **subid_grandparent** statements in the **global** document.
    The data in the CSV file will be inserted in
    ``Item`` elements under an ``ItemList`` element group. The subid
    will be entered as
    ``ListNumber`` elements for the items. The serial numbers
    in the CSV file must contain subid numbers.

    An example use for this mode was the creation of object LDHRM:2024.24, the
    collection of Ideal Home Exhibition postcards. The entire script is in file
    bin/make/2024-07-04_postcards.sh but the relevant extract follows::

        cat >tmp/in2.csv <<EOF
        Serial,Item Number,Title
        2024.24,1,The Gadgets
        2024.24,2,The Kitchen
        --etc--
        EOF
        cat >tmp/update2.yml <<EOF
        cmd: global
        add_mda_code:
        subid_column: Item Number
        subid_grandparent: .
        subid_parent: ItemList
        ---
        cmd: column
        xpath: Title
        EOF
        python src/update_from_csv.py tmp/normal/step1.xml tmp/normal/step2.xml -c tmp/update2.yml -m tmp/in2.csv -v 1

    This creates XML as follows::

        <ItemList>
            <Item>
                <ListNumber>1</ListNumber>
                <Title>The Gadgets</Title>
            </Item>
            <Item>
                <ListNumber>2</ListNumber>
                <Title>The Kitchen</Title>
            </Item>
            --etc--
        </ItemList>

    See the commands **subid_column**, **subid_parent**, and **subid_grandparent** in the
    :ref:`global_command` section in the configuration document.

"""
import argparse
from colorama import Fore, Style
from datetime import date
import os
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.cfgutil import Config, Stmt, Cmd, new_subelt, expand_idnum, process_if_other_column
from utl.location_sub import update_normal_loc, update_current_loc
from utl.normalize import normalize_id, sphinxify, denormalize_id
from utl.normalize import if_not_sphinx, DEFAULT_MDA_CODE
from utl.normalize import modes_person, modesdatefrombritishdate
import utl.normalize as nd
from utl.readers import row_dict_reader


def trace(level, template, *args, color=None):
    if _args.verbose >= level:
        if color:
            print(f'{color}{template.format(*args)}{Style.RESET_ALL}')
        else:
            print(template.format(*args))


def loadsubidvals(reader, allow_blanks) -> (dict, dict):
    """

    :param reader:
    :param allow_blanks:
    :return: 2-tuple of:
             (0) newval dict of accession numbers
             (1) subval dict with key of accession number with subid as in the CSV file
             without added MDA code (if applicable).
    """
    newval_dict = dict()
    subval_dict = dict()
    for row in reader:
        # print(f'{row=}')
        accnum = row[cfg.serial]
        if not accnum:
            if allow_blanks:
                trace(2, 'Row with blank accession number skipped: {}', row)
                continue  # skip blank accession numbers
            else:
                raise ValueError('Blank accession number in include file;'
                                 ' --allow_blank not selected.')
        naccnum = normalize_id(accnum)
        mainid, subid = nd.split_subid(naccnum)
        if subid is None:
            raise ValueError(f'Accession number "{accnum}" is missing the subid.')
        fullmainid = mainid
        if cfg.add_mda_code and mainid[0].isnumeric():
            fullmainid = _args.mdacode + '.' + mainid
        # Don't call expand_idnum as only a single subid is allowed.
        trace(2, 'loadsubidvals: mainid = {}, subid = {}', mainid, subid)
        newval_dict[normalize_id(fullmainid)] = None
        if naccnum in subval_dict:
            sys.tracebacklimit = 0
            raise ValueError(f'Duplicate subid: {accnum}')
        subval_dict[naccnum] = fullmainid, subid, row
    return newval_dict, subval_dict


def loadnewvals(reader, allow_blanks=False):
    newval_dict = {}
    for row in reader:
        # print(f'{row=}')
        accnum = row[cfg.serial]
        if not accnum:
            if allow_blanks:
                trace(2, 'Row with blank accession number skipped: {}', row)
                continue  # skip blank accession numbers
            else:
                raise ValueError('Blank accession number in include file;'
                                 ' --allow_blank not selected.')
        if cfg.add_mda_code and accnum[0].isnumeric():
            accnum = _args.mdacode + '.' + accnum
        accnums = expand_idnum(accnum)
        trace(3, 'loadnewvals: accnums = {}', accnums)
        for accnum in accnums:
            newval_dict[normalize_id(accnum)] = row
    return newval_dict


def add_item(elt, subid: int, nmainid: str) -> ET.Element:
    """
    For an existing parent (Usually ItemList) if there is an Item with the
    subid as a ListNumber, return the Item element. Otherwise, create an Item with a
    ListNumber equal to the subid and insert it in sort order in the list.
    :param elt:
    :param subid:
    :param nmainid: normalized ID without the subid
    :return: the existing or new Item element
    """
    olditem = elt.find(f'./Item[ListNumber="{subid}"]')
    if olditem is not None:
        return olditem
    items = list(elt)
    newitem = ET.Element('Item')
    list_number = ET.SubElement(newitem, 'ListNumber')
    list_number.text = str(subid)
    # We don't need the ObjectIdentity element as it can be inferred from
    # the main id and the list number.
    # object_identity = ET.SubElement(newitem, 'ObjectIdentity')
    # object_identity_number = ET.SubElement(object_identity, 'Number')
    # mainid = denormalize_id(nmainid)
    # object_identity_number.text = f'{mainid}.{subid}'
    if len(items) == 0:
        elt.append(newitem)
        return newitem
    # If the new item id is greater than the highest one on the list just
    # append it to the end.
    highest = items[-1].find('ListNumber')
    if highest is None:
        raise ValueError('Cannot find expected ListNumber')
    oldid = int(highest.text)
    if subid > oldid:
        elt.append(newitem)
        return newitem
    # Insert the new item before the first one that is greater.
    for n, item in enumerate(items):
        listnumberelt = item.find('ListNumber')
        if listnumberelt is None:
            raise ValueError('Cannot find expected ListNumber')
        oldid = int(listnumberelt.text)
        if subid < oldid:
            elt.insert(n, newitem)
            return newitem
    raise ValueError(f'Could not find where to insert the new element under {nmainid}')


def one_doc_aspect(objelem, idnum, doc):
    """
    Find all of the Aspect subelements under the xpath (the parent).
    If one has our Keyword, update the Reading.
    else if one has an empty Keyword, use that
    else create a new Aspect group. Add it to the end of the parent.
    """
    global nupdated, nunchanged, nequal
    parent = objelem.find(doc[Stmt.XPATH])
    title = doc[Stmt.TITLE]
    keyword_text = doc[Stmt.ASPECT]
    command = doc[Stmt.CMD]
    if command == Cmd.CONSTANT:
        reading_text = doc[Stmt.VALUE]  # we checked this in validate_yaml_cfg
    else:
        title = doc[Stmt.TITLE]
        reading_text = newvals[idnum][title]
        if not reading_text and not _args.empty:
            trace(3, '{}: empty Aspect field in CSV ignored. '
                     '--empty not specified', idnum)
            return
    if reading_text == '{{clear}}':
        reading_text = ''
    elif reading_text == '{{today}}':
        reading_text = _args.date
    aspects = list(parent.findall('Aspect'))  # make a list to use it twice
    found_aspect = False
    reading_elt = None
    # Look for an Aspect with our keyword
    for aspect in aspects:
        keyword_elt = aspect.find('Keyword')
        reading_elt = aspect.find('Reading')
        if keyword_elt is None or reading_elt is None:
            trace(2, '{}: Aspect element is missing a Keyword or Reading '
                  f'subelement. Ignored.', idnum)
            continue
        if keyword_elt.text == keyword_text:
            found_aspect = True
            break
    if not found_aspect:  # Search for empty Aspect groups
        for aspect in aspects:
            keyword_elt = aspect.find('Keyword')
            reading_elt = aspect.find('Reading')
            if keyword_elt is None or reading_elt is None:
                continue
            if not keyword_elt.text:
                keyword_elt.text = keyword_text
                found_aspect = True
                break
    if not found_aspect:
        # if there are existing Aspect elements, but not one suitable for
        # this keyword, create a new element group and insert it after the
        # existing Aspect(s). Otherwise append it to the parent.
        aspect = ET.Element('Aspect')
        keyword_elt = ET.SubElement(aspect, 'Keyword')
        reading_elt = ET.SubElement(aspect, 'Reading')
        keyword_elt.text = keyword_text
        if len(aspects) == 0:
            parent.append(aspect)
        else:
            insert_ix = None
            elts = list(parent)
            for n, e in enumerate(elts):
                if e.tag == 'Aspect':
                    insert_ix = n + 1
            if insert_ix is None:
                trace(0, '{}: Cannot find insert_after Aspect, ',
                      idnum, color=Fore.RED)
                raise ValueError('Internal error.')
            parent.insert(insert_ix, aspect)
    old_reading_text = reading_elt.text
    if old_reading_text and not _args.replace:
        if old_reading_text != reading_text:
            trace(1, '{} "{}" Aspect unchanged, old text: "{}",'
                     ' new text: "{}"\nSet --replace to force update.',
                  denormalize_id(idnum), title, old_reading_text,
                  reading_text, color=Fore.YELLOW)
        nunchanged += 1
        return False
    if old_reading_text and old_reading_text == reading_text:
        nequal += 1
        trace(2, '{} {}: Aspect unchanged: "{}" == "{}"',
              idnum, title, old_reading_text, reading_text)
        return False

    reading_elt.text = reading_text
    trace(3, '{} {}: Aspect Updated: "{}" -> "{}"', idnum,
          title, old_reading_text, reading_text)
    return True


def one_doc_location(objelem, idnum, doc):
    """

    :param objelem:
    :param idnum:
    :param doc:
    :return:
    """
    nidnum = normalize_id(idnum)
    if doc.move_to_normal:
        nl = objelem.find('./ObjectLocation[@elementtype="normal location"]')
        newlocationelt = nl.find('./Location')
        newloc = newlocationelt.text.strip().upper()
    else:
        csvrow = newvals[nidnum]
        loc_col = doc[Stmt.TITLE]
        newloc = csvrow[loc_col]
    if doc.update_normal:
        update_normal_loc(objelem, idnum, newloc, trace)
    if doc.update_current:
        if Stmt.DATE in doc:
            newdate = doc[Stmt.DATE]
        else:
            newdate = _args.date
        reason = doc.get(Stmt.REASON)
        update_current_loc(objelem, idnum, newloc, newdate, reason, trace)
    return


def one_element(objelem, idnum):
    """
    Update the fields specified by "column" configuration documents.
    Do not overwrite existing values unless --replace is specified.

    Note that we have already tested that idnum is in newvals.

    :param objelem: the Object
    :param idnum: the ObjectIdentity/Number text
    :return: True if updated, False otherwise
    """
    global nupdated, nunchanged, nequal, ndeleted
    updated = False
    for doc in cfg.col_docs:
        command = doc[Stmt.CMD]
        # print(f'{command=}')
        must_process = process_if_other_column(newvals[idnum], doc, idnum)
        trace(3, 'process... {} {} {}, must process: {}', idnum, command, doc[Stmt.TITLE], must_process)
        if not must_process:
            continue
        if Stmt.ASPECT in doc:
            aspect_updated = one_doc_aspect(objelem, idnum, doc)
            if aspect_updated:
                nupdated += 1
                updated = aspect_updated
            continue
        xpath = doc.get(Stmt.XPATH)  # previously checked that xpath is present if needed
        title = doc[Stmt.TITLE]
        if command == Cmd.DELETE:
            parent = objelem.find(doc[Stmt.PARENT_PATH])
            target = objelem.find(xpath)
            if target is not None:
                trace(2, '{}: Removing {}', idnum, xpath)
                parent.remove(target)
                ndeleted += 1
                updated = True
            continue
        elif command == Cmd.DELETE_ALL:
            targets = objelem.findall(xpath)
            if targets is not None:
                for target in targets:
                    trace(2, '{}: Removing {}', idnum, xpath)
                    objelem.remove(target)
                    ndeleted += 1
            continue
        elif command == Cmd.LOCATION:
            one_doc_location(objelem, idnum, doc)
            continue
        if command == Cmd.CONSTANT:
            target = objelem.find(xpath)
            if target is None:
                target = new_subelt(doc, objelem, idnum, _args.verbose)
                if target is None:  # parent is not specified or doesn't exist
                    trace(1, '{}: Cannot find target "{}", document "{}"', idnum,
                          xpath, title)
                    continue
            if Stmt.ATTRIBUTE in doc:
                target.set(doc[Stmt.ATTRIBUTE], doc[Stmt.ATTRIBUTE_VALUE])
            newtext = doc[Stmt.VALUE]
            target.text = newtext
            updated = True
            nupdated += 1
            continue
        # command is COLUMN
        newtext = newvals[idnum][title]
        # print(f'Command is column: {idnum=} {title=} {newtext=}')
        if not newtext and not _args.empty:
            trace(2, '{}: empty field ({}) in CSV ignored. --empty not specified',
                  idnum, title)
            continue
        target = objelem.find(xpath)
        if target is None:
            target = new_subelt(doc, objelem, idnum, _args.verbose)
            if target is None:  # parent is not specified or doesn't exist
                trace(1, '{}: Cannot find target "{}", document "{}"', idnum,
                      xpath, title)
                continue
        # get the text from the CSV column for this row
        oldtext = target.text
        if oldtext and not _args.replace:
            if oldtext != newtext:
                trace(1, '{} {} Unchanged, old text: "{}",'
                         ' new text: "{}"\nSet --replace to force update.',
                      denormalize_id(idnum), title, oldtext, newtext,
                      color=Fore.YELLOW)
            nunchanged += 1
            continue
        if oldtext and oldtext == newtext and not _args.force:
            nequal += 1
            trace(2, '{} {}: Unchanged: "{}" == "{}"', idnum, title,
                  oldtext, newtext)
            continue
        if newtext == '{{clear}}':
            newtext = ''
        elif newtext == '{{today}}':
            newtext = _args.date
        trace(3, '{} {}: Updated: "{}" -> "{}"', idnum, title, oldtext,
              newtext)
        if Stmt.NORMALIZE in doc:
            newtext = denormalize_id(newtext)
        elif Stmt.DATE in doc:
            # Only britishdate supported now
            try:
                newtext, _, _ = modesdatefrombritishdate(newtext)
                # print(type(elt.text))
            except ValueError:
                trace(2, 'Invalid date in {}: {}', idnum, newtext)
                newtext = 'unknown'
        elif Stmt.PERSON_NAME in doc:
            newtext = modes_person(newtext)
        target.text = newtext
        updated = True
        nupdated += 1
    return updated


def one_element_subid_mode(nidnum: str, objelem: ET.Element):
    """

    :param nidnum: normalized accession number of object
    :param objelem:
    :return:
    """
    trace(4, 'nidnum = {}', nidnum, color=Fore.GREEN)
    grandparent = objelem.find(cfg.subid_grandparent)
    if grandparent is None:
        raise ValueError(f'Cannot find grandparent path: '
                         f'"{cfg.subid_grandparent}" of "{nidnum}"')
    parent = grandparent.find(cfg.subid_parent)  # usually ItemList
    if parent is None:
        parent = ET.SubElement(grandparent, cfg.subid_parent)
    for idnum, val in subvals.items():
        # print(f'{val=}')
        mainid, subid, row = val
        if mainid != nidnum:
            continue
        newitem = add_item(parent, subid, mainid)
        for doc in cfg.col_docs:
            newelt = ET.SubElement(newitem, doc[Stmt.XPATH])
            if doc[Stmt.CMD] == Cmd.COLUMN:
                newelt.text = row[doc[Stmt.TITLE]]
            else:  # cmd: constant
                newelt.text = doc[Stmt.TITLE]


def main():
    global nwritten
    outfile.write(b'<?xml version="1.0" encoding="UTF-8"?><Interchange>\n')
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find(cfg.record_id_xpath)
        idnum = idelem.text if idelem is not None else None
        nidnum = normalize_id(idnum)
        trace(4, 'idnum: {}', idnum)
        if nidnum and nidnum in newvals:
            trace(4, 'nidnum: {}', nidnum, color=Fore.GREEN)
            if cfg.subid_parent is not None:
                one_element_subid_mode(nidnum, elem)
                updated = True
            else:
                updated = one_element(elem, nidnum)
                del newvals[nidnum]
        else:
            updated = False
            if _args.missing:
                trace(2, 'Not in CSV file: "{}"', idnum)
        trace(4, 'updated....... {}', updated)
        if updated or _args.all:
            outfile.write(ET.tostring(elem, encoding='utf-8'))
            nwritten += 1
        if updated and _args.short:
            break
    outfile.write(b'</Interchange>\n')
    # if it's not subid mode and we're not debugging, then trace the serial
    # numbers in the CSV file that did not result in XML updates.
    if cfg.subid_parent is None and not _args.short:
        for nidnum in newvals:
            trace(1, 'In CSV but not XML: "{}"', denormalize_id(nidnum))


def getparser():
    parser = argparse.ArgumentParser(description='''
        Read a CSV file containing two or more column_paths. The first column
        is the index and the following columns are the field(s) defined by the
        XPATH statement in the YAML configuration file. Update the
        XML file with data from the CSV file. The CSV file must contain
        a heading row with column titles matching the ``title`` statements
        in the YAML configuration file.''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects. The default is to only write updated objects.''')
    parser.add_argument('--allow_blanks', action='store_true', help='''
        Skip rows in the include CSV file with blank accession numbers. If not
        set, this will cause an abort. ''')
    parser.add_argument('-c', '--cfgfile', required=True,
                        type=argparse.FileType(), help='''
        Required. The YAML configuration file describing the column path(s) to
         update''')
    parser.add_argument('-d', '--date', help='''
        If a column in the CSV file contains '{{today}}', use this value for
        the field text. The default is today’s date.
        ''')
    parser.add_argument('-e', '--empty', action='store_true', help=sphinxify('''
        Normally, an empty field in the CSV file means that no action is to be
        taken. If -e is selected, empty values from the CSV will overwrite
        the fields in the file. Another way to do this for specific fields is
        to set the text to ``{{clear}}`` in the CSV field to be emptied.
        --empty implies --replace.''', called_from_sphinx))
    parser.add_argument('-f', '--force', action='store_true', help='''
         If set, replace existing fields even if they are identical. This is needed
         in case a field like a date or person name will undergo transformation.''')
    parser.add_argument('--missing', action='store_true', help='''
        By default, ignore indices missing from the CSV file. If selected,
        trace the missing index. Useful if you are updating all objects.''')
    parser.add_argument('-m', '--mapfile', required=True, help=sphinxify('''
        Required. The CSV file mapping the object number to the new element
        value(s). The file may also be an Excel spreadsheet with a filename
        ending ``.xlsx``. The
        first column must contain the object number and subsequent columns
        must have headers that correspond to the titles of the columns in the
        configuration
        file. If a row in the CSV file has fewer fields than defined in the
        configuration file, zero-length strings will be assumed. See
        --empty. To do: make this optional in which case all objects will
        be selected. This is useful to add a constant value to all objects.
        In the meantime, use ``xml2csv.py`` with no configuration
        file which will generate a CSV file will all accession numbers.
        ''', called_from_sphinx))
    parser.add_argument('--mdacode', default=DEFAULT_MDA_CODE,
                        help=sphinxify(f'''
        Specify the MDA code, used if the accession number in the CSV file
        is specified without the leading MDA code. You must also specify
        the global statement ``add_mda_code`` in the YAML config file.''',
                                       called_from_sphinx) +
                        if_not_sphinx(f''' The default is "{DEFAULT_MDA_CODE}".
                        ''', called_from_sphinx))
    parser.add_argument('-r', '--replace', action='store_true', help=sphinxify('''
        Replace existing values. If not specified only empty elements will be
        updated. Existing values will be cleared if the value in the CSV file
        contains the special value ``{{clear}}``. See also --empty. If
        --replace is not set a warning will be issued if the existing value
        is not blank.''', called_from_sphinx))
    parser.add_argument('--serial', default='Serial', deprecated=True,
                        help=sphinxify('''
        The column containing the serial number must have a heading with this
        value. This argument is deprecated. Use the
        ``serial:`` global configuration statement.''' + if_not_sphinx('''
        The default value is "Serial".''', called_from_sphinx),
                                       called_from_sphinx))
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('--skiprows', type=int, default=0, help=sphinxify('''
        Skip rows at the beginning of the CSV file specified by --mapfile.
        ''', called_from_sphinx))
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    if args.empty:
        args.replace = True
    if os.path.splitext(args.mapfile)[1].lower() not in ('.csv', '.xlsx'):
        raise ValueError('mapfile must be a CSV or Excel file.')
    if args.date:
        args.date, _, _ = modesdatefrombritishdate(args.date)
    else:
        args.date = nd.modesdate(date.today())
    return args


def check_cfg(config: Config):
    errs = 0
    for doc in config.col_docs:
        cmd = doc[Stmt.CMD]
        if cmd == Cmd.DELETE:
            if Stmt.PARENT_PATH not in doc:
                trace(1, 'The parent_path: statement is required for the delete command.')
                errs += 1
            for stmt in doc:
                # Note some statements are created internally if they are not
                # explicitly specified in the config.
                if stmt not in (Stmt.CMD, Stmt.XPATH, Stmt.TITLE,
                                Stmt.MULTIPLE_DELIMITER, Stmt.PARENT_PATH,
                                Stmt.ELEMENT, Stmt.COLUMN_TITLE):
                    trace(1, 'Delete command: Statement "{}" not allowed, '
                             'ignored', stmt, color=Fore.RED)
                    errs += 1
        elif cmd not in (Cmd.COLUMN, Cmd.CONSTANT):
            trace(1, 'Command "{}" not allowed, ignored', cmd, color=Fore.RED)
            errs += 1
        elif (Stmt.ATTRIBUTE in doc) ^ (Stmt.ATTRIBUTE_VALUE in doc):
            trace(1, 'cmd: {}: attribute statement requires '
                  'attribute_value:', cmd, color=Fore.RED)
            errs += 1
    for doc in config.ctrl_docs:  # "global" is not in this dict
        trace(1, 'Control command "{}" not allowed, ignored.', doc[Stmt.CMD],
              color=Fore.RED)
        errs += 1
    return errs


def sq(val):
    return '' if val == 1 else 's'


called_from_sphinx = True
if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    called_from_sphinx = False
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    nupdated = nunchanged = nwritten = nequal = ndeleted = 0
    trace(1, 'Begin update_from_csv.', color=Fore.GREEN)
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}\nCreating file: {}', _args.infile, _args.outfile)
    cfg = Config(_args.cfgfile, dump=_args.verbose > 1)
    if errors := check_cfg(cfg):
        trace(1, '{} command{} ignored.', errors, 's' if errors > 1 else '')
        trace(1, 'update_from_csv aborting due to config error(s).',
              color=Fore.RED)
        sys.exit(1)
    if not cfg.serial:
        cfg.serial = _args.serial
    csvreader = row_dict_reader(_args.mapfile, _args.verbose, _args.skiprows)
    if cfg.subid_parent is not None:
        newvals, subvals = loadsubidvals(csvreader, allow_blanks=_args.allow_blanks)
    else:
        newvals = loadnewvals(csvreader, allow_blanks=_args.allow_blanks)
        subvals = None  # for trace
    trace(4, 'newvals = {}\nsubvals = {}', newvals, subvals, color=Fore.YELLOW)
    nnewvals = len(newvals) if newvals else 0
    main()
    trace(1, '{} element{} in {} object{} updated.\n'
          '{} existing element{} unchanged.\n'
          '{} element{} updated where new == old.\n'
          '{} element{} deleted.',
          nupdated, sq(nupdated),
          nnewvals, sq(nnewvals),
          nunchanged, sq(nunchanged),
          nequal, sq(nequal),
          ndeleted, sq(ndeleted))
    trace(1, 'End update_from_csv. {} objects written.', nwritten,
          color=Fore.GREEN)
