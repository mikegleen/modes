#!/bin/zsh
#
#   Return the Sublime picture back to the store
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
INXML=/Users/mlg/pyprj/hrm/modes/prod_save/normal/2026-03-17s_prod_save_sorted.xml
echo INXML = $INXML
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
OUTFILE=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
cat>tmp/$SCRIPT.csv <<EOF
Serial
JB644
JB629
JB641
LDHRM.2019.32
JB425
JB607
JB430
LDHRM.2019.35
LDHRM.2019.21
LDHRM.2019.31
EOF
python src/location.py update \
                        --infile $INXML \
                        --outfile prod_update/normal/$OUTFILE \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --mapfile tmp/$SCRIPT.csv \
                        --move_to_normal \
                        --reason 'return from sublime exhibition' \
                        --date 28.2.2026
bin/syncupdate.sh
bin/syncdelta.sh
