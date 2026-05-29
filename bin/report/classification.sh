#!/bin/zsh
set -e
INXML=$(python src/utl/x066_latest.py -i prod_update/normal)
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
OUTCSV=tmp/$SCRIPT.csv
# echo  SCRIPT = $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: global
skip_number:
---
cmd: multiple
title: Classification
xpath: ./Identification/Classification/Keyword
---
EOF
python src/xml2csv.py $INXML tmp/step1.csv -b -c tmp/$SCRIPT.yml
cat >tmp/${SCRIPT}_step2.py <<EOF
import sys
print('starting ${SCRIPT}_step2', file=sys.stderr)
for row in open("tmp/step1.csv"):
    keywords = [kw.strip() for kw in row.split('|')]
    for kw in keywords:
        print(kw)
EOF
python tmp/${SCRIPT}_step2.py >tmp/step2.csv
sort tmp/step2.csv |uniq >results/reports/${SCRIPT}_termlist.csv
sort tmp/step2.csv |uniq -c>tmp/step3.csv  # count occurrences
cat >tmp/step3.py <<EOF
# Convert "1 keyword" to "1,keyword"
import re
infile = open('tmp/step3.csv')
outfile = open('results/reports/${SCRIPT}_termlist_count.csv', 'w')
for row in infile:
    print(re.sub(r'(\s*[0-9]+)? (.*)', r'\1,\2', row.strip()), file=outfile)
EOF
python tmp/step3.py
