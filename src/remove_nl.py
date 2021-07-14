"""
    Remove \n characters from CSV fields.
"""
import csv
import sys

infile = open(sys.argv[1])
outfile = open(sys.argv[2], 'w')

reader = csv.reader(infile)
writer = csv.writer(outfile)

for row in reader:
    newrow = []
    for cell in row:
        newrow.append(cell.replace('\n', ' '))
    writer.writerow(newrow)
