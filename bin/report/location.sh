#!/bin/zsh
set -e
pushd /Users/mlg/pyprj/hrm/modes
cat >tmp/dirs.csv <<EOF
prod_save/normal
prod_update/normal
EOF
INXML=$(python src/utl/x066_latest.py -f tmp/dirs.csv)
echo INXML = $INXML
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
OUTCSV=tmp/$SCRIPT.csv
cat >tmp/$SCRIPT.yml <<EOF
column: Current
xpath: ./ObjectLocation[@elementtype="current location"]/Location
---
column: Normal
xpath: ./ObjectLocation[@elementtype="normal location"]/Location
---
cmd: column
xpath: ./Identification/Title
EOF
cat>tmp/$SCRIPT.csv <<EOF
Serial
LDHRM.2022.35
JB392a
LDHRM.2021.13
JB383
JB387
JB1114
JB1105.1
JB1105.4
JB1105.5
EOF
python src/xml2csv.py $INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading --include tmp/$SCRIPT.csv
