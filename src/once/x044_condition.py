"""
    Update the <Condition> element. Remove the text under Condition and insert
    the text in a new <Keyword> subelement.
"""

import io
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from utl.cfgutil import Config, new_subelt
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
        cond = obj.find('./Description/Condition')
        if cond is not None and cond.text:
            condtext = cond.text
            cond.text = ''
            keywd = new_subelt(cfg.col_docs[0], obj, idnum)
            keywd.text = condtext
        outfile.write(ET.tostring(obj))


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    infile = sys.argv[1]
    outfile = open(sys.argv[2], 'wb')
    outfile.write(b'<?xml version="1.0"?><Interchange>\n')
    main()
    outfile.write(b'</Interchange>')

