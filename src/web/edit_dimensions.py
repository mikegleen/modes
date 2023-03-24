#
#   Height, Width -> HxWmm
#

import csv

infilename = '/Users/mlg/pyprj/hrm/collection/etc/batch017update/batch017_add_dimensions.csv'
outfilename = '/Users/mlg/pyprj/hrm/collection/etc/batch017update/batch017_add_dimensions2.csv'

inreader = csv.reader(open(infilename))
outwriter = csv.writer(open(outfilename, 'w'))

for row in inreader:
    if not row[1]:
        continue
    newrow = [row[0], f'{row[1]}x{row[2]}mm']
    outwriter.writerow(newrow)
