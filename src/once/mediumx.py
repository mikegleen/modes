# -*- coding: utf-8 -*-
"""
    Search XML for all variations on Production/Method and Inscription/Material/Keyword
    (where Inscription/Material/Part == "medium").
    Report cases where the Method and Keyword values are different.
"""
from collections import defaultdict
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars


def main():
    s = defaultdict(int)
    snum = defaultdict(list)
    s2 = defaultdict(int)
    s2num = {}
    print('\nReport of non-matching Production and Description values')
    for event, elem in ET.iterparse(infile):
        idelem = elem.find('./ObjectIdentity/Number')
        idnum = idelem.text if idelem is not None else None
        if elem.tag != 'Object':
            continue
        method = elem.find('./Production/Method')
        if method is not None and method.text:
            s[method.text] += 1
            snum[method.text].append(idnum)
        materials = elem.findall('./Description/Material')
        for material in materials:
            part = material.find('./Part')
            if part.text == 'medium':
                keywords = material.findall('./Keyword')
                for keyword in keywords:
                    if keyword.text:
                        if keyword.text != method.text:
                            print(f'no match {idnum}:',
                                  f'"{method.text}" ≠ "{keyword.text}"')
                        s2[keyword.text] += 1
                        s2num[keyword.text] = idnum
    print('\n------Production/Material:')
    for method in sorted(s):
        idnum = ','.join(snum[method]) if s[method] < 20 else ''
        print(f'"{method}"  {s[method]} {idnum}')
    # print('\n------Description/Material/Keyword:')
    # for method in sorted(s2):
    #     idnum = s2num[method] if s2[method] == 1 else ''
    #     print(f'"{method}"  {s2[method]} {idnum}')


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    infile = open(sys.argv[1])
    main()

