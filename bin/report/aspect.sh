#!/bin/zsh
set -e
INXML=/Users/mlg/pyprj/hrm/modes/prod_save/normal/2025-09-10_prod_save_sorted.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
OUTCSV=tmp/$SCRIPT.csv
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: if
xpath: ./Description/Aspect[Keyword="pages"]
title: ifAspect
---
cmd: column
xpath: ./Description/Aspect
title: Aspect
---
cmd: column
xpath: ./Description/Aspect/Reading
EOF
python src/xml2csv.py $INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
