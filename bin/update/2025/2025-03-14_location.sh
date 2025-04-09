#!/bin/zsh
#
#   Update normal locations from unknown
#
set -e
INXML=2025-03-08_stocktake_condition.xml
#
#   Manual changes applied:
# 2018.19 Move <Note> element outside of Date element group.
#
# Change:
#    <ObjectLocation elementtype="previous location">
#        <Location>R7</Location>
#        <Date>
#            <DateBegin>29.11.2024</DateBegin>
#            <DateEnd>5.3.2025</DateEnd>
#            <Note>Stocktake 2024 (Patched)</Note>
#        </Date>
#    </ObjectLocation>
# To:
#    <ObjectLocation elementtype="previous location">
#        <Location>R7</Location>
#        <Date>
#            <DateBegin>29.11.2024</DateBegin>
#            <DateEnd>5.3.2025</DateEnd>
#        </Date>
#        <Note>Stocktake 2024 (Patched)</Note>
#    </ObjectLocation>
#
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
