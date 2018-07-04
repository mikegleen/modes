# -*- coding: utf-8 -*-
"""
For the XML file created by Modes, convert
    <ObjectLocation elementtype="home location">
to
    <ObjectLocation elementtype="normal location"> 
"""

import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

ETYPE = 'elementtype'


def handle_object(object_elem):
    for e in object_elem.findall('ObjectLocation'):
        try:
            if e.attrib[ETYPE] == 'home location':
                e.set(ETYPE, 'normal location')
        except KeyError:
            pass

infile = open(sys.argv[1])
outfile = open(sys.argv[2], 'w')

outfile.write('<?xml version="1.0"?><Interchange>')

for event, elem in ET.iterparse(infile):
    if elem.tag == 'Object':
        handle_object(elem)
        s = ET.tostring(elem, encoding='unicode')
        obj = []
        for line in s.split('\n'):
            # tostring() has prettyprinted the element. Undo that
            line = re.sub(r'\s+', ' ', line).strip()
            obj.append(line)
        outfile.write(''.join(obj))
        elem.clear()
        outfile.write('\n')  # newline after every Object

outfile.write('</Interchange>')
