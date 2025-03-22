#!/bin/zsh
#
#   Update normal locations from unknown
#
set -e
INXML=2025-03-08_stocktake_condition.xml
#
#   Manual changes applied:
# 2018.19 Move <Note> element outside of Date element group.
#         Add note to normal location.
#
INXML=2025-03-08_stocktake_loc2.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('/')[-1].split('.')[0])")
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
cat >tmp/$SCRIPT.csv <<EOF
Serial,Location
2018.19,G18
2024.11,R8
2024.13,R8
EOF
python src/location.py update -i prod_update/normal/$INXML -o prod_update/normal/$OUTXML -a \
                        --mapfile tmp/$SCRIPT.csv --normal
#
python src/location.py update -i prod_update/normal/$INXML -o prod_delta/normal/$DELTAXML \
                        --mapfile tmp/$SCRIPT.csv --normal
#
bin/syncupdate.sh
bin/syncdelta.sh
