"""
    Find duplicated columns in a CSV file.
    Input is the CSV file produced by csv2xml.py using title_and_briefdes.yml

"""
import csv
import sys

TESTCOL = 1

infile = open(sys.argv[1])
reader = csv.reader(infile)
origdict = dict()

for row in reader:
    target = row[TESTCOL]
    if target in origdict:
        print(f'dup: {origdict[target]} {row[0]}')
    else:
        origdict[target] = row[0]
