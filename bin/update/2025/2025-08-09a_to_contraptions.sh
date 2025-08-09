#!/bin/zsh
#
#   Move objects to JBG for Contraptions
#
set -e
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
INMAP=tmp/update.csv
INCFG=tmp/update.yml
#
# Input XML file containing the full database in prod_update/normal/
INXML=2025-08-09_jb1105.xml
#
# Directory definitions
#
INPUTDIR=prod_update/normal
NEWOBJDIR=prod_make/normal
OUTPUTDIR=prod_update/normal
#
# Output XML file containing the new Object records in prod_make/normal/
OUTXML=$OUTPUTDIR/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
#
#
cat >tmp/update.yml <<EOF
cmd: location
location_type: current
date: 26.7.2025
reason: Contraption and Connections Exhibition
value: JBG
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
python src/update_from_csv.py $INPUTDIR/$INXML \
                              --outfile $OUTXML \
                              --deltafile $DELTAXML \
                              --cfgfile $INCFG \
                              --mapfile $INMAP -v 1
# python src/location.py update -i $INPUTDIR/$INXML \
#                               -o $OUTXML \
#                               --deltafile $DELTAXML \
#                               --location JBG \
#                               --current \
#                               --reason 'Contraption and Connections Exhibition' \
#                               --mapfile $INMAP \
#                               --date 26.7.2025
bin/syncdelta.sh
bin/syncupdate.sh
