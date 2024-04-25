#!/bin/zsh
set -e
INXML=2024-04-07_JB119.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
cat >tmp/$SCRIPT.yml <<EOF
cmd: ifexhib
value: 34
---
cmd: column
xpath: ./ObjectLocation[@elementtype="normal location"]/Location
title: Normal Loc
---
cmd: column
xpath: ./Identification/Title
---
# cmd: column
# xpath: ./Identification/BriefDescription
# ---
EOF
python src/xml2csv.py prod_update/normal/$INXML results/reports/$SCRIPT.csv -c tmp/$SCRIPT.yml --heading -b
