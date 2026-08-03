#!/bin/bash
#
#   Move LDHRM.2024.11, LDHRM.2024.13 to G5.
#
INXML=prod_save/pretty/2026-08-02s_prod_save_sorted_pretty.xml
#
source ~/pyprj/hrm/modes/bin/boilerplate.sh
cat>tmp/${SCRIPT}_mapfile.csv <<EOF
Serial
LDHRM.2024.11
LDHRM.2024.13
EOF
python src/location.py update \
                        --infile $INXML \
                        --outfile prod_update/normal/$OUTFILE \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --mapfile tmp/${SCRIPT}_mapfile.csv \
                        --normal --current \
                        --location G5 \
                        --date 30.7.2026 \
                        --verbose 2
bin/syncupdate.sh
bin/syncdelta.sh
