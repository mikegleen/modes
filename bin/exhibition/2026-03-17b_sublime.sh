#!/bin/zsh
#
#   Detail input is a CSV file created from the object movement record:
#       2025-10-27_HRM_Object movement_Sublime Space.docx
#       Table 2
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
cat >tmp/dirs.csv <<EOF
prod_save/normal
prod_update/normal
EOF
INXML=prod_update/normal/2026-03-17a_location.xml
echo INXML = $INXML
#
#   bin/exhibition/2026-03-15_sublime.sh -> 2026-03-15_sublime
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
EXHIBITION=43
#
cat >tmp/$SCRIPT.csv <<EOF
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
python src/exhibition.py    $INXML \
                            --mapfile tmp/$SCRIPT.csv \
                            --outfile prod_update/normal/$OUTXML \
                            --deltafile prod_delta/normal/$DELTAXML \
                            --exhibition $EXHIBITION \
                            --verbose 1
#
bin/syncupdate.sh
bin/syncdelta.sh
