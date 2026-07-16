#!/bin/bash
#
#   Return the Line of Life pictures back to the store.
#   The list of objects is the same as bin/exhibition/2026-03-17d_line.sh
#   with added Spodnoodle objects at the end
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
INXML=prod_update/normal/2026-07-15_line.xml
SCRIPT="$(basename -- "${0%.*}")"
OUTFILE=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
echo INXML = $INXML
echo OUTXML=$OUTFILE
cat>tmp/$SCRIPT.csv <<EOF
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
JB617
JB616
JB310
#
# Spodnoodle drawings added in a second batch.
#
JB146
JB464
SH68.5
SH68.12
SH68.14
EOF
python src/location.py update \
                        --infile $INXML \
                        --outfile prod_update/normal/$OUTFILE \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --mapfile tmp/$SCRIPT.csv \
                        --move_to_normal \
                        --reason 'returned from Line of Life exhibition' \
                        --date 4.7.2026 \
                        --verbose 2
bin/syncupdate.sh
bin/syncdelta.sh
