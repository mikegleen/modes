#!/bin/zsh
#
#   Move pictures to JBG for the Sublime exhibition
#
set -e
INXML=/Users/mlg/pyprj/hrm/modes/prod_update/normal/2025-11-06_jbg.xml
#
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('/')[-1].split('.')[0])")
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
cat >tmp/$SCRIPT.csv <<EOF
Serial
JB641
LDHRM.2019.32
JB425
JB607
JB430
JB642
JB435
LDHRM.2019.35&21&31
EOF
python src/location.py update -i $INXML -o prod_update/normal/$OUTXML \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --reason 'sublime exhibition' \
                        --mapfile tmp/$SCRIPT.csv \
                        --date 1.11.2025 \
                        --location "Joan Brinsmead Gallery" --current
#
bin/syncupdate.sh
bin/syncdelta.sh
