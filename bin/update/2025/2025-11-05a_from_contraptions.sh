#!/bin/zsh
#
#   Move objects from JBG back to store
#   Add Exhibition elements for the objects
#
set -e
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
INMAP=tmp/update.csv
INCFG=tmp/update.yml
#
# Path of input XML file containing the full database
INXML=$(python src/utl/x066_latest.py -i prod_update/normal)
#
OUTXML_STEP1=tmp/${SCRIPT}_step1.xml
OUTXML=prod_update/normal/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
#
cat >tmp/update.yml <<EOF
cmd: location
location_type: move_to_normal
date: 5.11.2025
reason: Move Contraption and Connections Exhibition pictures back to store
# value: JBG
# title: location
EOF
#
cat >tmp/update.csv <<EOF
Serial
LDHRM.2022.35
JB392a
LDHRM.2021.13
JB383
JB387
JB1114
JB1105.1
JB1105.4
JB1105.5
EOF
python src/update_from_csv.py $INXML \
                              --outfile $OUTXML_STEP1 \
                              --cfgfile $INCFG \
                              --mapfile $INMAP -v 1
#
python src/exhibition.py $OUTXML_STEP1 -o $OUTXML \
                         --deltafile $DELTAXML \
                         --exhibition 42 \
                         --mapfile $INMAP
#
bin/syncdelta.sh
bin/syncupdate.sh
