#!/bin/zsh
#
#
set -e
INCLUDE_FILE=data/location/2025-06-05_antiques_road_show.csv
INXML=prod_update/normal/2025-04-03a_county.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
STEPHENSXML=tmp/normal/${SCRIPT}_stephens.xml
OUTXML=prod_update/normal/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
#
python src/exhibition.py $INXML -o $STEPHENSXML \
                         --mapfile $INCLUDE_FILE \
                         --exhibition 41 \
                         --move_to_location
python src/location.py update -i $STEPHENSXML -o $OUTXML \
                       --deltafile $DELTAXML \
                       --mapfile $INCLUDE_FILE \
                       --date 4.6.2025 \
                       --current
bin/syncupdate.sh
bin/syncdelta.sh
