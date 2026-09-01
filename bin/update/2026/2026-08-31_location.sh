#!/bin/bash
#
#   Move framed pictures from R5 to R4
#
INXML=prod_save/normal/2026-08-31s_prod_save_sorted.xml
MAPFILE=data/object_movement/2026-08-29_Modes_location_change_R4.xlsx
#
source ~/pyprj/hrm/modes/bin/boilerplate.sh
python src/location.py update \
                        --infile $INXML \
                        --outfile prod_update/normal/$OUTFILE \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --mapfile $MAPFILE \
                        --normal --current \
                        --col_acc 'Object number' \
                        --location R4 \
                        --date 28.8.2026 \
                        --verbose 1
bin/syncupdate.sh
bin/syncdelta.sh
