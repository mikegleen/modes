#!/bin/zsh
#
#   Add the condition data from the stocktake spreadsheet
#
set -e
INXML=2025-03-05_prod_sorted.xml
INCSV=data/stocktake/2025-03-08_Stocktake.xlsx
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
cat >tmp/update.yml <<EOF
cmd: global
serial: Accession Number
---
column: Condition
xpath: ./Description/Condition/Note
EOF
#
python src/update_from_csv.py prod_update/normal/$INXML \
                              prod_update/normal/$OUTXML \
                              -c tmp/update.yml -m $INCSV -v 1 -a --allow_blank
python src/update_from_csv.py prod_update/normal/$INXML \
                              prod_delta/normal/$DELTAXML \
                              -c tmp/update.yml -m $INCSV -v 1 --allow_blank
bin/syncupdate.sh
bin/syncdelta.sh

