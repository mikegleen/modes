#!/bin/zsh
set -e
INXML=2024-04-27d_mottisfont.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
OUTCSV=tmp/$SCRIPT.csv
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: ifattribeq
xpath: .
attribute: elementtype
value: Original Artwork
---
cmd: ifnot
xpath: ./Description/Measurement[Part="Image"]/Reading
---
cmd: constant
value:
xpath: .
title: H x W
---
cmd: column
xpath: ./ObjectLocation[@elementtype="current location"]/Location
---
cmd: column
xpath: ./Identification/Title
width: 50
---
EOF
python src/xml2csv.py prod_update/normal/$INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
