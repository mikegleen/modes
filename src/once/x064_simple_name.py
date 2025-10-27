"""
    Update the <Production/Place> element. Remove the children <County> and <Country>.
"""

import io
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.readers import object_reader


def main(idnum, obj):
    identification = obj.find('./Identification')  # will barf if doesn't exist
    if identification is None:  # delete the elementtype=placeholder objects
        print(f'{idnum=}')
        return
    simple_name: ET.Element = identification.find('./ObjectName[@elementtype="simple name"]')
    if simple_name is None:
        simple_name = ET.SubElement(identification, 'ObjectName', attrib={'elementtype': 'simple_name'})
    keyword = simple_name.find('Keyword')
    if keyword is None:
        keyword = ET.SubElement(simple_name, 'Keyword')
    idtype = identification.find('./Type')
    if keyword.text is None:
        if idtype is None or idtype.text is None:
            keyword.text = obj.attrib['elementtype']
        else:
            keyword.text = idtype.text
    if idtype is not None:
        identification.remove(idtype)

    outfile.write(ET.tostring(obj))


if __name__ == '__main__':
    assert sys.version_info >= (3, 13)
    infile = sys.argv[1]
    outfile = open(sys.argv[2], 'wb')
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    for id_num, ob_ject in object_reader(infile):
        main(id_num, ob_ject)
    outfile.write(b'</Interchange>')

