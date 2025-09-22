#!/bin/zsh
#
#   Move letters etc from G12 to G7 to make room for JB1224
#
set -e
INXML=/Users/mlg/pyprj/hrm/modes/prod_update/normal/2025-09-11_aspect.xml
#

SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('/')[-1].split('.')[0])")
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
cat >tmp/$SCRIPT.csv <<EOF
Serial,loctype
2024.24,n
2021.19&22,c
EOF
python src/location.py update -i $INXML -o prod_update/normal/$OUTXML \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --reason 'reorganize folders' \
                        --mapfile tmp/$SCRIPT.csv \
                        --date 13.9.2025 \
                        --location G7 --col_loc_type loctype
#
bin/syncupdate.sh
bin/syncdelta.sh
