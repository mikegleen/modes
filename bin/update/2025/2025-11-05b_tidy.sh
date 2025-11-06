#!/bin/zsh
#
#   Record a objects moved between locations in the store.
#
set -e
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
INMAP=tmp/update.csv
INCFG=tmp/update.yml
INXML=prod_update/normal/2025-11-05a_from_contraptions.xml
OUTXML=prod_update/normal/$SCRIPT.xml
#
cat >tmp/update.yml <<EOF
cmd: location
location_type: current
date: 5.11.2025
reason: Move within the store
location_column: Location
EOF
#
cat >tmp/update.csv <<EOF
Serial,Location
LDHRM.2024.1-5,G7
LDHRM.2023.19,G18
EOF
python src/update_from_csv.py $INXML \
                              --outfile $OUTXML \
                              --deltafile tmp/delta.xml \
                              --cfgfile $INCFG \
                              --mapfile $INMAP -v 1
#
bin/syncdelta.sh
bin/syncupdate.sh
