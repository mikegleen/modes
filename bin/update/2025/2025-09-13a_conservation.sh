#!/bin/zsh
#
#   Update location of pictures going out for conservation
#
set -e
INXML=/Users/mlg/pyprj/hrm/modes/prod_update/normal/2025-09-13_location.xml
#

SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('/')[-1].split('.')[0])")
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
cat >tmp/$SCRIPT.csv <<EOF
Serial
2023.16-18
EOF
python src/location.py update -i $INXML -o prod_update/normal/$OUTXML \
                        --deltafile prod_delta/normal/$DELTAXML \
                        --reason 'Adopt a Picture' \
                        --mapfile tmp/$SCRIPT.csv \
                        --date 13.9.2025 \
                        --location conservation \
                        --current
#
bin/syncupdate.sh
bin/syncdelta.sh
