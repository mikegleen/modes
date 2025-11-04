#!/bin/zsh
set -e
INXML=2025-09-13a_conservation.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
OUTCSV=tmp/$SCRIPT.csv
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: ifattribeq
xpath: .
attribute: elementtype
value: Original Artwork
---
cmd: column
xpath: ./Identification/Title
---
EOF
python src/xml2csv.py prod_update/normal/$INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
