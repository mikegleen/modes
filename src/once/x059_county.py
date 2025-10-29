"""
    Update the <Production/Place> element. Remove the children <County> and <Country>.
"""

import io
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfgutil import Config
from utl.readers import object_reader as obr

cfgtext = '''
cmd: column
xpath: ./Description/Condition/Keyword
parent_path: ./Description/Condition
insert_after:
'''


def main():
    cfgfile = io.StringIO(cfgtext)
    cfg = Config(cfgfile)
    for idnum, obj in obr(infile, cfg):
        place: ET.Element = obj.find('./Production/Place')
        if place is not None:
            county = place.find('./County')
            if county is not None:
                place.remove(county)
            country = place.find('./Country')
            if country is not None:
                place.remove(country)
        outfile.write(ET.tostring(obj))


if __name__ == '__main__':
    assert sys.version_info >= (3, 13)
    infile = sys.argv[1]
    outfile = open(sys.argv[2], 'wb')
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    main()
    outfile.write(b'</Interchange>')

