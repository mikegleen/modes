"""
    Remove brackets from around dates
"""

import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.readers import object_reader


def parsedate(text) -> (int, str):
    if text is None or '[' not in text:
        return 0, text
    m = re.match(r'\[(\d{4})\]', text)  # [1935]
    if m:
        return 1, m[1]
    m = re.match(r'\[(\d{4})\?\]', text)  # [1935?]
    if m:
        return 2, m[1]
    m = re.match(r'\[(\d{3})-\?\]', text)  # [193-?]
    if m:
        return 3, m[1] + '0'
    return 4, text


def setsubelts(dateelt, accuracytext):
    if accuracytext:
        accuracy = dateelt.find('./Accuracy')
        if accuracy is None:
            accuracy = ET.SubElement(dateelt, 'Accuracy')
            accuracy.text = accuracytext
    keyword = ET.SubElement(dateelt, 'Keyword')
    keyword.text = 'bracketed'


def setcases(dateelt, datecase):
    match datecase:
        case 0:
            pass
        case 1:  # [1935]
            setsubelts(dateelt, None)
        case 2:  # [1935?]
            setsubelts(dateelt, 'circa')
        case 3:  # [193-?]
            setsubelts(dateelt, 'decade')


def main(idnum, obj):
    dateelt = obj.find('./Production/Date[@elementtype="publication date"]')
    if dateelt is None:
        outfile.write(ET.tostring(obj))
        return
    datebegin = dateelt.find('./DateBegin')
    if datebegin is not None:
        datecase, text = parsedate(datebegin.text)
        datebegin.text = text
        setcases(dateelt, datecase)
    else:
        datecase, text = parsedate(dateelt.text)
        dateelt.text = text
        setcases(dateelt, datecase)
    outfile.write(ET.tostring(obj))
    return


if __name__ == '__main__':
    assert sys.version_info >= (3, 13)
    infile = sys.argv[1]
    outfile = open(sys.argv[2], 'wb')
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    for id_num, ob_ject in object_reader(infile):
        # print(f'{ob_ject=}')
        main(id_num, ob_ject)
    outfile.write(b'</Interchange>')

