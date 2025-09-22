#!/bin/zsh
#
#   Move page numbers from Aspect.text to Aspect/Reading.text
#
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
EOF
#
python src/xml2csv.py $INXML $OUTCSV --bom --cfgfile tmp/$SCRIPT.yml --heading
#
cat >tmp/${SCRIPT}.yml <<EOF
column: Aspect
xpath: ./Description/Aspect/Reading
---
cmd: constant
xpath: ./Description/Aspect
value:
title: setaspect
EOF
#
python src/update_from_csv.py $INXML --outfile prod_update/normal/$SCRIPT.xml \
                                     --deltafile prod_delta/normal/${SCRIPT}_delta.xml \
                                     --cfgfile tmp/${SCRIPT}.yml \
                                     --mapfile $OUTCSV \
                                     --replace
bin/syncupdate.sh
bin/syncdelta.sh
