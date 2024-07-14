#!/bin/zsh
set -e
INXML=2024-07-05_postcards.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
OUTCSV=tmp/$SCRIPT.csv
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: ifcontains
xpath: ./Production/SummaryText
value: motorist
---
cmd: column
xpath: ./Identification/Title
---
cmd: column
xpath: ./Production/SummaryText
title: Summary
EOF
python src/xml2csv.py prod_update/normal/$INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
