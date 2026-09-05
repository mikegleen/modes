#!/bin/bash
#
#   Move framed pictures from R5 to R4
#
INXML=prod_save/normal/2026-09-02s_prod_save_sorted.xml
#
source ~/pyprj/hrm/modes/bin/boilerplate.sh
python src/location.py update \
                        --infile $INXML \
                        --outfile prod_update/normal/$OUTFILE \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --normal --current \
                        --object '2023.7' \
                        --location R1 \
                        --date 28.8.2026 \
                        --verbose 1
bin/syncupdate.sh
bin/syncdelta.sh
