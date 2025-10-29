"""
    Update the <Exhibition> element. Remove the text under Place and insert
    the text in a new <PlaceName> subelement.
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
        exhibs = obj.findall('./Exhibition')
        for exhibnum, exhib in enumerate(exhibs, start=1):
            place = exhib.find('./Place')
            text = place.text
            if not text:
                continue
            place.text = None
            placename = ET.SubElement(place, 'PlaceName')
            placename.text = text
        outfile.write(ET.tostring(obj))


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    infile = sys.argv[1]
    outfile = open(sys.argv[2], 'wb')
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    main()
    outfile.write(b'</Interchange>')

