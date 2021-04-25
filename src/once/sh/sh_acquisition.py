"""
    For all SH objects, update the Acquisition group to set:
    Method: purchase
    Organization/OrganizationName: Stancliffe and Glover
    Organization/Role: purchased from
    Funding/Note: Purchased with the assistance of the National Heritage
                Memorial Fund and the ArtFund

    For objects listed in CSVFILE, add:
    <Conservation>
        <SummaryText>Conserved with the
                assistance of the Association of Independent Museums.
        </SummaryText>
    </Conservation>

    For objects listed in CONSFILE, add the Reason element
"""
import argparse
import codecs
import csv
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
import sys

from utl.cfgutil import Stmt
from utl.normalize import normalize_id

CSVFILE = 'results/csv/2021-04-12_sh_conserved.csv'
CONDFILE = 'results/csv/hr_at_war_condition.csv'


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def make_conserved() -> tuple[set[str], dict[str]]:
    confile = codecs.open(CSVFILE, 'r', 'utf-8-sig')
    trace(1, 'using list of conserved objects in: {}', confile.name)
    conserved = set()
    for row in confile:
        row = row.strip()
        if not (row.startswith('SH') or row.startswith('JB')):
            row = 'SH' + row
        normid = normalize_id(row)
        if normid in conserved:
            print(f'Duplicate id: {normid}')
        conserved.add(normid)
    print(f'{len(conserved)=}')
    condfile = codecs.open(CONDFILE, 'r', 'utf-8-sig')
    trace(1, 'using condition of conserved objects in: {}', condfile.name)
    condition = dict()
    reader = csv.reader(condfile)
    for row in reader:
        normid = normalize_id(row[0])
        if normid in condition:
            print(f'Duplicate id: {normid}')
        condition[normid] = row[1]
    print(f'{len(condition)=}')
    return conserved, condition


def new_org():
    newelt = ET.Element('Organization')
    subelt = ET.SubElement(newelt, 'OrganizationName')
    subelt.text = 'Stancliffe and Glover'
    subelt = ET.SubElement(newelt, 'Role')
    subelt.text = 'purchased from'
    return newelt


def one_object(objelt: ET.Element, idnum: str, conserved: set[str],
               condition: dict[str]):
    """

    :param objelt:
    :param idnum:
    :param conserved: set of id numbers to add conservation info to
    :param condition: dict of id->text taken from CONDFILE
    :return: The updated object if successful, else None
    """
    global nconserved
    if idnum in conserved:
        conserved.remove(idnum)
        conselt = objelt.find('./Conservation')
        if conselt is None:
            trace(1, 'No Conservation element in {}.', idnum)
            return None
        sumtext = ET.Element('SummaryText')
        sumtext.text = ('Conserved with the assistance of the Association of '
                        'Independent Museums.')
        conselt.append(sumtext)
        nconserved += 1
        if idnum in condition:
            reason = ET.Element('Reason')
            reason.text = condition[idnum]
            conselt.append(reason)
    if idnum.startswith('JB'):
        return objelt
    acq = objelt.find('./Acquisition')
    if acq is None:
        trace(1, 'Object {} has no Acquisition element.', idnum)
        return None
    person = acq.find('./Person')
    if person is not None:
        acq.remove(person)
    acqelts = list(acq)
    orgindex = -1
    for n, acqsubelt in enumerate(acqelts):
        if acqsubelt.tag == 'Method':
            acqsubelt.text = 'purchase'
            orgindex = n + 1  # index for the Organization element
            break
    if orgindex >= 0:
        acq.insert(orgindex, new_org())
    else:  # didn't find a Method element
        trace(2, "Creating Method for {}", idnum)
        method = ET.Element('Method')
        method.text = 'purchase'
        acq.insert(0, method)
        acq.insert(1, new_org())
    funding = acq.find('./Funding')
    if funding is None:
        trace(1, 'No find funding: {}', idnum)
        return None
    summarytext = ET.Element('SummaryText')
    summarytext.text = ('Purchased with the assistance of the National '
                        'Heritage Memorial Fund and the ArtFund.')
    funding.append(summarytext)
    cons = acq.find('./SummaryText[@elementtype="Conservation text"]')
    if cons is not None:
        acq.remove(cons)


def main():
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    written = 0
    numupdated = 0
    conserved, condition = make_conserved()
    for event, elem in ET.iterparse(infile):
        if elem.tag != 'Object':
            continue
        idelem = elem.find(Stmt.get_default_record_id_xpath())
        idnum = idelem.text if idelem is not None else None
        idnum = normalize_id(idnum)
        trace(3, 'idnum: {}', idnum)
        updated = False
        if idnum.startswith('SH') or idnum == 'JB00000314':
            one_object(elem, idnum, conserved, condition)
            updated = True
            numupdated += 1
        if updated or _args.all:
            outfile.write(ET.tostring(elem, encoding='utf-8'))
            written += 1
        if updated and _args.short:
            break
    outfile.write(b'</Interchange>')
    trace(1, f'End SH_acquisition.py. {written} object'
             f'{"s" if written != 1 else ""} written '
             f'of which {numupdated} updated.')
    for idnum in conserved:
        print(f'Not processed: {idnum}')


def getargs():
    parser = argparse.ArgumentParser(description='''
    For all SH objects, update the Acquisition group.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
        Write all objects. The default is to only write updated objects.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process a single object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    nconserved = 0
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    trace(1, 'Input file: {}', _args.infile)
    trace(1, 'Creating file: {}', _args.outfile)
    main()
    trace(1, '{} conserved.', nconserved)
