#!/bin/bash
#
#   Move JB447 to R1.
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
INXML=prod_update/normal/2026-07-16_unseen.xml
SCRIPT="$(basename -- "${0%.*}")"
OUTFILE=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
echo INXML = $INXML
echo OUTXML=$OUTFILE
#
cat>tmp/${SCRIPT}_mapfile.csv <<EOF
Serial
JB447
EOF
python src/location.py update \
                        --infile $INXML \
                        --outfile prod_update/normal/$OUTFILE \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --mapfile tmp/${SCRIPT}_mapfile.csv \
                        --normal --current \
                        --location R1 \
                        --verbose 2
bin/syncupdate.sh
bin/syncdelta.sh
