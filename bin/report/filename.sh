#!/bin/zsh
set -e
INXML=2024-02-01d_G1_to_G2.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
OUTCSV=tmp/$SCRIPT.csv
echo SCRIPT: $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: ifelt
xpath: ./References/Filename
title: Filenameif
---
cmd: column
xpath: ./Identification/Title
---
cmd: column
xpath: ./References/Filename
title: Filename
EOF
python src/xml2csv.py prod_update/normal/$INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
