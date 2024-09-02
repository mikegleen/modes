"""
    Add location information to the spreadsheet.
"""
import codecs
import csv
import sys

from utl.cfgutil import expand_idnum

inmaster = codecs.open(sys.argv[1], encoding='utf-8-sig')
outmaster = codecs.open(sys.argv[2], 'w', encoding='utf-8-sig')

OLDFIELDS = ('Serial,Pages,Date,Person From,Person To,Org From,Org To,'
             'Type,Comment,Description'.split(','))
NEWFIELDS = ('Serial,Pages,Date,Person From,Person To,Org From,Org To,'
             'Type,Comment,Location,Description'.split(','))
print(f'{OLDFIELDS=}')
print(f'{NEWFIELDS=}')

locs = """G8 JB1204&6&11&13
G9 JB1203&8&9&7&28
G10 JB1202&18&19&20&21&10&12
G10 JB1205A
G11 JB1205B"""
loclist = locs.split('\n')

locdict = {}

for row in loclist:
    loc, assns = row.split()
    # print(assns)
    assnlist = expand_idnum(assns)
    for assn in assnlist:
        locdict[assn] = loc
    print(loc, assnlist)

outwriter = csv.DictWriter(outmaster, NEWFIELDS)
outwriter.writeheader()
for row in csv.DictReader(inmaster):
    assns = row['Serial'].split('.')  # JB001.1 -> ['JB001', '1']
    assn = assns[0]
    if assn in locdict:
        row['Location'] = locdict[assn]
    else:
        row['Location'] = 'N/A'
    # print(row)
    outwriter.writerow(row)
