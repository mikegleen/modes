"""
    This test demonstrates that embedded line feeds are preserved within quoted CSV fields.
"""


import csv
import io

data = '''a,b,c
1,"Width: 44mm
Height: 66mm",test embedded line feed
2,"Width: 44mm
Height: ""66""mm",test quote escaped by doubling
'''

infile = io.StringIO(data)
reader = csv.DictReader(infile)
for i, row in enumerate(reader):
    print(f'{i}. ::{row}::')
    for k, v in row.items():
        print(f'({k})', v)
