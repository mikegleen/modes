#!/bin/zsh
#
#   Detail input is a CSV file created from the object movement record:
#       2026-02-27_HRM_Object movement_The LIFE in a Line!.docx
#       Table 2
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
cat >tmp/dirs.csv <<EOF
prod_save/normal
prod_update/normal
EOF
INXML=prod_save/normal/2026-03-17s_prod_save_sorted.xml
echo INXML = $INXML
#
#   bin/exhibition/2026-03-15_sublime.sh -> 2026-03-15_sublime
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
EXHIBITION=44
#
cat >tmp/$SCRIPT.csv <<EOF
Serial
JB169
JB175
SH35
SH34
SH68
JB392a
JB391
SH25
LDHRM.2021.7
JB619
SH325
SH101
JB362
SH314
022
JB617
JB616
JB310
EOF
python src/exhibition.py    $INXML \
                            --mapfile tmp/$SCRIPT.csv \
                            --outfile prod_update/normal/$OUTXML \
                            --deltafile prod_delta/normal/$DELTAXML \
                            --exhibition $EXHIBITION \
                            --move_to_location \
                            --location 'Joan Brinsmead Gallery' \
                            --verbose 1
#
bin/syncupdate.sh
bin/syncdelta.sh
