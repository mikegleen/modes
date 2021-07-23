"""
    Find duplicated titles in a CSV file created from a Modes XML file.
    Input CSV files were produced by csv2xml.py using title_and_briefdes.yml
    :parameter: CSV file of serial, title from original XML file
    :parameter: CSV file of serial, title from modified XML file
    :parameter: CSV with output list
"""
import csv
import sys
from utl.normalize import normalize_id

infile = open(sys.argv[1])
reader = csv.reader(infile)
titledict = dict()  # title -> serial
origdict = dict()  # serial -> original title
newtitles = dict()
culprits = set()
pairs = list()


def norm(e):
    return normalize_id(e[0])


for row in reader:
    title = row[1]
    if title in titledict:
        oldserial = titledict[title]
        newserial = row[0]
        culprits.add(oldserial)
        origdict[oldserial] = title
        culprits.add(newserial)
        pairs.append((oldserial, newserial))
    else:
        titledict[title] = row[0]

infile.close()
infile = open(sys.argv[2])
reader = csv.reader(infile)

for row in reader:
    serial = row[0]
    title = row[1]
    briefdes = row[2]
    if serial in culprits:
        newtitles[serial] = (title, briefdes)

outfile = open(sys.argv[3], 'w')
writer = csv.writer(outfile)
heading = ('Serial 1', 'Serial 2', 'Original Title', 'New Title 1',
           'New Title 2', 'Brief Description 1', 'Brief Description 2')
writer.writerow(heading)
pairs.sort(key=norm)
for row in pairs:
    oldserial = row[0]
    newserial = row[1]
    outrow = (oldserial, newserial, origdict[oldserial],
              newtitles[oldserial][0], newtitles[newserial][0],
              newtitles[oldserial][1], newtitles[newserial][1])
    writer.writerow(outrow)
