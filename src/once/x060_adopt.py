"""
    Modify the Association/Type/Person/Name (Adopt a Picture) element to be ../PersonName
"""

import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.readers import object_reader


def main():
    for idnum, obj in object_reader(infile):
        personname: ET.Element = obj.find('./Association[Type="Adopt a Picture"]/Person/Name')
        if personname is not None:
            personname.tag = "PersonName"
        outfile.write(ET.tostring(obj))


if __name__ == '__main__':
    assert sys.version_info >= (3, 13)
    infile = sys.argv[1]
    outfile = open(sys.argv[2], 'wb')
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    main()
    outfile.write(b'</Interchange>')
