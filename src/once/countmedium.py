# -*- coding: utf-8 -*-
"""

"""
import csv
import sys

incsvfile = open(sys.argv[1], newline='')
reader = csv.reader(incsvfile)
d = set()
for row in reader:
    if 'Baa' in row[2]:
        break
    d.add(row[2])
for m in sorted(d):
    print(m)
