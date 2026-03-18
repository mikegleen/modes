#!/bin/zsh
#
#   Two of the pictures in the Sublime exhibition were not moved there. Fix that.
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
INXML=/Users/mlg/pyprj/hrm/modes/prod_update/normal/2026-03-17_revert.xml
echo INXML = $INXML
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
OUTFILE=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
cat>tmp/$SCRIPT.csv <<EOF
Serial
JB644
JB629
EOF
# JB641
# LDHRM.2019.32
# JB425
# JB607
# JB430
# LDHRM.2019.35
# LDHRM.2019.21
# LDHRM.2019.31
# EOF
python src/location.py update \
                        --infile $INXML \
                        --outfile prod_update/normal/$OUTFILE \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --mapfile tmp/$SCRIPT.csv \
                        --current \
                        --location 'Joan Brinsmead Gallery' \
                        --reason 'sublime exhibition' \
                        --date 1.11.2025
bin/syncupdate.sh
bin/syncdelta.sh
