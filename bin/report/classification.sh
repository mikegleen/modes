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
cmd: if
xpath: ./Identification/Classification/Keyword
---
cmd: multiple
title: Classification
xpath: ./Identification/Classification/Keyword
---
EOF
# python src/xml2csv.py $INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml
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
sort tmp/step2.csv |uniq -c>tmp/step3.csv
cat >tmp/step3.py <<EOF
import re
infile = open('tmp/step3.csv')
outfile = open('results/reports/${SCRIPT}_termlist.csv', 'w')
for row in infile:
    print(re.sub(r'(\s*[0-9]+)? (.*)', r'\1,\2', row.strip()), file=outfile)
EOF
python tmp/step3.py
