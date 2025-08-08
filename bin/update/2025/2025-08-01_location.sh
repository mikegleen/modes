#!/bin/zsh
#
#   Move pictures from JBG back to store
#
set -e
INXML=prod_save/normal/2025-08-07_prod_save_sorted.xml
#

SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('/')[-1].split('.')[0])")
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
cat >tmp/$SCRIPT.csv <<EOF
Serial,Location
JB105,R4
JB623,S6
SH41,S11
EOF
python src/location.py update -i $INXML -o prod_update/normal/$OUTXML \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --current \
                        --reason 'returned from Ways of Seeing' \
                        --mapfile tmp/$SCRIPT.csv \
                        --date 20.7.2025 \
                        --col_loc Location
#
bin/syncupdate.sh
bin/syncdelta.sh
