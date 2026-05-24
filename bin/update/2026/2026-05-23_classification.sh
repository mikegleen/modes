#!/bin/zsh
#
# Reformat Classification elements
#
# Step 1. Extract Classification keywords and reformat various formats to
#       keyword|keyword|...
#
# Input: XML file with one or more Classification elements each with one or more Keyword elements.
#        Each Keyword element can have one or more keywords separated by either "," or ";".
#
set -e
INXML=$(python src/utl/x066_latest.py -i prod_save/normal)
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
# echo  SCRIPT = $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: global
# skip_number:
---
cmd: if
xpath: ./Identification/Classification/Keyword
---
cmd: multiple
title: Classification
xpath: ./Identification/Classification/Keyword
---
EOF
#
# Produce a CSV file with the serial number in column 1 and keywords in column 2
# separated by "|" characters.
#
python src/xml2csv.py $INXML tmp/$SCRIPT.csv -b -c tmp/$SCRIPT.yml
#
# For each Keyword element extract the "sub-keywords" separated by "," or ";".
#
cat >tmp/$SCRIPT.py <<EOF
import csv
infile = open('tmp/$SCRIPT.csv', encoding='utf-8-sig')
reader = csv.reader(infile)
outfile = open('tmp/${SCRIPT}_expanded.csv', 'w')
print(f'{infile=}, {outfile=}')
writer = csv.writer(outfile)
writer.writerow(('Serial', 'Keywords'))
for row in reader:
    serial = row[0]
    keys = row[1].split('|')
    semis = []
    for key in keys:
        for semi in key.split(';'):
            if semi not in semis:
                semis.append(semi)
    commas = []
    for s in semis:
        for c in [ss.strip() for ss in s.split(',')]:
            if c not in commas:
                commas.append(c)
    print(f'{row=}')
    print(f'{commas=}')
    writer.writerow((serial, '|'.join(commas)))
# print('outfile', 'tmp/${SCRIPT}_expanded2.csv')
EOF
python tmp/$SCRIPT.py >tmp/log.txt
