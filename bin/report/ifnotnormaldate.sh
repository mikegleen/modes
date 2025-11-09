#!/bin/zsh
set -e
INXML=$(python src/utl/x066_latest.py -i prod_update/normal)
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
OUTCSV=tmp/$SCRIPT.csv
cat >tmp/$SCRIPT.yml <<EOF
cmd: ifnot
xpath: ./ObjectLocation[@elementtype="normal location"]/Location
---
EOF
python src/xml2csv.py $INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
