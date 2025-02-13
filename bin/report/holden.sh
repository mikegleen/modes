#!/bin/zsh
set -e
INXML=2025-01-30_location.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
OUTCSV=tmp/$SCRIPT.csv
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: ifeq
xpath: ./Acquisition/Person/PersonName
value: Patrick Holden
---
cmd: column
xpath: ./Identification/Title
---
cmd: column
xpath: ./Description/Condition/Note
title: Condition
EOF
python src/xml2csv.py prod_update/normal/$INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
