#!/bin/zsh
set -e
pushd /Users/mlg/pyprj/hrm/modes
cat >tmp/dirs.csv <<EOF
prod_save/normal
prod_update/normal
EOF
INXML=$(python src/utl/x066_latest.py -f tmp/dirs.csv)
echo INXML = $INXML
# SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
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
JB641
LDHRM.2019.32
JB425
JB607
JB430
JB644
JB629
LDHRM.2019.35
LDHRM.2019.21
LDHRM.2019.31
EOF
python src/xml2csv.py $INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading --include tmp/$SCRIPT.csv
