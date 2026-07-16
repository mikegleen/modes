#!/bin/zsh
#
#   Add additional objects that were displayed in the Life in a Line exhibition
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
INXML=prod_save/normal/2026-07-15s_prod_save_sorted.xml
echo INXML = $INXML
#
#   bin/exhibition/2026-03-15_sublime.sh -> 2026-03-15_sublime
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
EXHIBITION=44
#
MAPFILE=tmp/$SCRIPT.csv
cat >$MAPFILE <<EOF
Serial
JB146
JB464
SH68.5
SH68.12
SH68.14
EOF
python src/exhibition.py    $INXML \
                            --mapfile $MAPFILE \
                            --outfile prod_update/normal/$OUTXML \
                            --deltafile prod_delta/normal/$DELTAXML \
                            --exhibition $EXHIBITION \
                            --move_to_location \
                            --location 'Joan Brinsmead Gallery' \
                            --verbose 1
#
bin/syncupdate.sh
bin/syncdelta.sh
