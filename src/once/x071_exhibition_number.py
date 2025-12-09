"""
    Insert <ObjectName elementtype="simple name"> elements into all objects.
"""
import codecs

import os
import time
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.readers import object_reader
from utl.exhibition_list import (get_inverted_exhibition_dict, ExhibitionTuple)
from utl.normalize import datefrommodes


def tuple_from_element_group(exhibition_elt: ET.Element):
    exhibition_name = catalogue_number = placename = datebegin = dateend = None
    subelts = list(exhibition_elt)
    for subelt in subelts:
        tag = subelt.tag
        match tag:
            case 'ExhibitionName':
                exhibition_name = subelt.text
            case 'CatalogueNumber':
                catalogue_number = subelt.text
            case 'Place':
                placenameelt = subelt.find('./PlaceName')
                if placenameelt is not None:
                    placename = placenameelt.text
            case 'Date':
                datebeginelt = subelt.find('./DateBegin')
                if datebeginelt is not None and datebeginelt.text:
                    datebegin, _ = datefrommodes(datebeginelt.text)
                dateendelt = subelt.find('./DateEnd')
                if dateendelt is not None and dateendelt.text:
                    dateend, _ = datefrommodes(dateendelt.text)
            case 'ExhibitionNumber':
                pass
            case _:
                print('Unknown subelt:', tag)
    if not (datebegin or dateend or exhibition_name or placename):
        return None
    extuple = ExhibitionTuple(datebegin, dateend, exhibition_name, placename)
    return extuple


def main(idnum, obj):
    exhibs = obj.findall('./Exhibition')
    # found = False
    for exhib in exhibs:
        # found = True
        extuple = tuple_from_element_group(exhib)
        if extuple is None:  # empty Exhibition
            # found = False
            continue
        exhib_num = str(exinvdict.get(extuple))
        if exhib_num:
            exhib_num_elt = ET.SubElement(exhib, 'ExhibitionNumber')
            exhib_num_elt.text = exhib_num
        else:
            print('Cannot find exhibition number:', idnum)
            print(f'{extuple=}')
    ET.ElementTree(obj).write(outfile, encoding="unicode")
    return


if __name__ == '__main__':
    assert sys.version_info >= (3, 13)
    print(f"Begin {os.path.basename(sys.argv[0])}.")
    t1 = time.perf_counter()
    exinvdict = get_inverted_exhibition_dict()
    infile = sys.argv[1]
    # codecs.open('testunicode.xml', "w", "utf-8-sig")
    # outfile = open(sys.argv[2], 'w', "utf-8-sig")
    outfile = open(sys.argv[2], 'w', encoding="utf-8")
    outfile.write('<?xml version="1.0" encoding="UTF-8"?><Interchange>\n')
    for id_num, ob_ject in object_reader(infile):
        main(id_num, ob_ject)
    outfile.write('</Interchange>')
    elapsed = time.perf_counter() - t1
    print(f'Elapsed: {elapsed:6.3f} seconds.')
