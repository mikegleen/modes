"""
    Reformat size information from '123x456' to '123mm x 456mm'
"""
import codecs
import csv
import re
import sys


inmaster = codecs.open(sys.argv[1], encoding='utf-8-sig')
outmaster = codecs.open(sys.argv[2], 'w', encoding='utf-8-sig')

NEWFIELDS = ('Serial,H x W,Location'.split(','))
SIZEKEY = 'Size mm HxW'
skiprow = next(inmaster)
# outmaster.write(skiprow)
reader = csv.DictReader(inmaster)
outwriter = csv.DictWriter(outmaster, reader.fieldnames)
outwriter.writeheader()
for row in reader:
    for key, cell in row.items():
        row[key] = row[key].replace('\n', ' ').strip()
    hxw = row[SIZEKEY]
    print(f'{hxw=}')
    if hxw:
        m = re.match(r'([\d.]+)\s*[Xx]\s*([\d.]+)', hxw)
        if m:
            row[SIZEKEY] = f'{m[1]}mm x {m[2]}mm'
        else:
            print('nomatch', hxw)
    outwriter.writerow(row)
