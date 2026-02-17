#!/bin/zsh
#
#   Move pictures to JBG for the Sublime exhibition
#
set -e
INXML=/Users/mlg/pyprj/hrm/modes/prod_update/normal/2026-01-13_book.xml
#
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
cat >tmp/$SCRIPT.csv <<EOF
Serial
JB457
JB465
JB467
EOF
python src/location.py update -i $INXML -o prod_update/normal/$OUTXML \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --reason 'removed from mount' \
                        --mapfile tmp/$SCRIPT.csv \
                        --location "BB1" --current --normal
#
bin/syncupdate.sh
bin/syncdelta.sh
