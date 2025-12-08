"""
    Insert <ObjectName elementtype="simple name"> elements into all objects.
"""
import os
import time
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from utl.readers import object_reader


def main(idnum, obj):
    identification = obj.find('./Identification')
    if identification is None:
        print(f'No Identificaiton: {idnum} (elementtype={obj.get('elementtype')})')
        outfile.write(ET.tostring(obj))
        return
    simplename = identification.find('./ObjectName[@elementtype="simple name"]')
    if simplename is None:
        simplename = ET.Element('ObjectName')
        simplename.set('elementtype', 'simple name')
        identification.insert(0, simplename)
    keyword = simplename.find('./Keyword')
    if keyword is None:
        keyword = ET.SubElement(simplename, 'Keyword')
    if not keyword.text:
        keyword.text = obj.get('elementtype')
        idtype = identification.find('./Type')
        if idtype is not None:
            if idtype.text:
                keyword.text = idtype.text
            identification.remove(idtype)
    othername = identification.find('./ObjectName[@elementtype="other name"]')
    if othername is not None:
        # remove it if the keyword is not populated.
        keyword = othername.find('./Keyword')
        if keyword is None or not keyword.text:
            identification.remove(othername)
    outfile.write(ET.tostring(obj))
    return


if __name__ == '__main__':
    assert sys.version_info >= (3, 13)
    print(f"Begin {os.path.basename(sys.argv[0])}.")
    t1 = time.perf_counter()
    infile = sys.argv[1]
    outfile = open(sys.argv[2], 'wb')
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    for id_num, ob_ject in object_reader(infile):
        main(id_num, ob_ject)
    outfile.write(b'</Interchange>')
    elapsed = time.perf_counter() - t1
    print(f'Elapsed: {elapsed:6.3f} seconds.')
