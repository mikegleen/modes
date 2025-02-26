#!/bin/zsh
set -e
INXML=2025-02-07_stocktake_loc.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
OUTCSV=tmp/$SCRIPT.csv
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: global
# skip_number:
---
cmd: if
xpath: ./Description/Aspect
---
cmd: column
xpath: ./Description/Aspect/Keyword
---
# cmd: column
# xpath: ./Identification/Title
# width: 50
# ---
EOF
python src/xml2csv.py prod_update/normal/$INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
