#!/bin/bash
#
#   Return the conserved pictures back to the store
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
INXML=prod_save/normal/2026-04-08t_prod_save_sorted.xml
SCRIPT="$(basename -- "${0%.*}")"
OUTFILE=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
echo INXML = $INXML
echo OUTXML=$OUTFILE
cat>tmp/$SCRIPT.csv <<EOF
Serial
LDHRM.2023.15-19
LDHRM.2023.21
EOF
python src/location.py update \
                        --infile $INXML \
                        --outfile prod_update/normal/$OUTFILE \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --mapfile tmp/$SCRIPT.csv \
                        --move_to_normal \
                        --reason 'returned from conservation' \
                        --date 8.4.2026 \
                        --verbose 2
bin/syncupdate.sh
bin/syncdelta.sh
