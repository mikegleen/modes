# -*- coding: utf-8 -*-
"""
    Framework for ad hoc queries into a Modes XML file.
"""
import resource
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def one_object(elt):
    # e = elt.find('./Production/Organisation/Role')
    # e = elt.find('./Description/Condition/Note')
    e = elt.find('./Content/Person/Role')
    if e is not None and e.text:
        e = elt.find('./ObjectIdentity/Number')
        print(e.text)


def main():
    for event, obj in ET.iterparse(infile):
        if obj.tag == 'Object':
            one_object(obj)
            obj.clear()


if __name__ == '__main__':
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    infile = open(sys.argv[1])
    r = resource.getrusage(resource.RUSAGE_SELF)
    print(r.ru_maxrss)
    main()
    print(r.ru_maxrss)
