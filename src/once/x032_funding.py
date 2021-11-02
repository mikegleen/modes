# -*- coding: utf-8 -*-
"""
Convert:
    <Acquisition>
        <Method>purchase</Method>
        <Organisation>
            <OrganisationName>Stancliffe and Glover</OrganisationName>
            <Role>purchased from</Role>
        </Organisation>
        <Date />
        <Funding elementtype="Sponsorship">
            <SummaryText>Purchased with the assistance of the National Heritage Memorial Fund and the ArtFund</SummaryText>
        </Funding>
        <SummaryText elementtype="Acquisition text">Bought from the estate of Simon Heneage through their agents Stancliffe and Glover</SummaryText>
        <SummaryText elementtype="Conservation text" />
    </Acquisition>

to
    <Acquisition>
        <Method>purchase</Method>
        <Date>3.2015</Date>
        <Funding>Purchased with the assistance of the National Heritage Memorial Fund and the ArtFund</Funding>
        <SummaryText>Bought from the estate of Simon Heneage through their agents Stancliffe and Glover</SummaryText>
    </Acquisition>

"""
import argparse
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

SUMMARY_TEXT = ('Bought from the estate of Simon Heneage through their'
                ' agents Stancliffe and Glover')
FUNDING_TEXT = ('Purchased with the assistance of the National Heritage'
                ' Memorial Fund and the ArtFund')
ACQUISITION_DATE = '3.2015'


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_sh_object(obj):
    """
    Recreate the Acquisition element of all SH objects.
    :param obj:
    :return: True if updated
    """
    acquisition = obj.find('./Acquisition')
    for child in list(acquisition):
        acquisition.remove(child)
    method = ET.SubElement(acquisition, 'Method')
    method.text = 'purchase'
    date = ET.SubElement(acquisition, 'Date')
    date.text = ACQUISITION_DATE
    funding = ET.SubElement(acquisition, 'Funding')
    funding.text = FUNDING_TEXT
    summary_text = ET.SubElement(acquisition, 'SummaryText')
    summary_text.text = SUMMARY_TEXT
    return True


def one_other_object(obj):
    """
    Recreate the Acquisition element of all SH objects.
    :param obj:
    :return: True if updated
    """
    acquisition = obj.find('./Acquisition')
    if acquisition is None:
        return
    funding = acquisition.find('./Funding[@elementtype="Sponsorship"]')
    if funding is not None:
        del funding.attrib['elementtype']
    sumtext = acquisition.find('./SummaryText[@elementtype="Acquisition text"]')
    if sumtext is not None:
        del sumtext.attrib['elementtype']
    sumtext = acquisition.find('./SummaryText[@elementtype="Conservation text"]')
    if sumtext is not None:
        acquisition.remove(sumtext)
    return True


def main():
    global object_number
    outfile.write(b'<?xml version="1.0" encoding="utf-8"?>\n<Interchange>\n')
    for event, oldobject in ET.iterparse(infile):
        if oldobject.tag != 'Object':
            continue
        numelt = oldobject.find('./ObjectIdentity/Number')
        if numelt is not None:
            object_number = numelt.text
        else:
            object_number = 'Missing'
            trace(1, 'Missing "{}"', object_number)
        trace(2, '**** {}', object_number)
        updated = False
        if object_number.startswith('SH'):
            updated = one_sh_object(oldobject)
        else:
            updated = one_other_object(oldobject)
        outfile.write(ET.tostring(oldobject, encoding='us-ascii'))
        if updated and _args.short:  # for debugging
            return
        oldobject.clear()
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
    Add Acquisition information to SHnnn records.
        ''')
    parser.add_argument('infile', help='''
        The XML file saved from Modes.''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-s', '--short', action='store_true', help='''
        Only process one object. For debugging.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    object_number = None
    csvdict = {}  # The rows from the CSV file indexed by Serial
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    main()
