#!/bin/zsh
#
#   Reformat the <Condition> element group to not use the <Keyword>
#   element. Convert:
#
# <Condition>
# <Note/>
# <Keyword>fair</Keyword>
# </Condition>
#
# to:
#
# <Condition>
# fair
# <Note/>
# </Condition>
#
set -e
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo ZSH_ARGZERO: $ZSH_ARGZERO
echo SCRIPT: $SCRIPT
INMAP=tmp/update.csv
#
# Input XML file containing the full database in prod_update/normal/
#
INXML=2025-08-09a_to_contraptions.xml
#
# Directory definitions
#
INPUTDIR=prod_update/normal
NEWOBJDIR=prod_make/normal
UPDATEDIR=prod_update/normal
DELTADIR=prod_delta/normal
#
# Output XML file containing the new Object records in prod_make/normal/
OUTXML=$UPDATEDIR/$SCRIPT.xml
DELTAXML=$DELTADIR/${SCRIPT}_delta.xml
#
#
cat >tmp/report.yml <<EOF
cmd: ifattribnoteq
xpath: .
attribute: elementtype
value: placeholder
---
cmd: ifattribnoteq
xpath: .
attribute: elementtype
value: object group
---
column: Condition
xpath: ./Description/Condition/Keyword
EOF
#
cat >tmp/update.csv <<EOF
EOF
#
#   Create a CSV file with the text from the Condition element
#
python src/xml2csv.py $INPUTDIR/$INXML tmp/$SCRIPT.csv \
                      --cfgfile tmp/report.yml \
                      --heading
#
cat >tmp/update.yml <<EOF
cmd: delete
xpath: ./Description/Condition/Keyword
parent_path: ./Description/Condition
title: delete_keyword
---
column: Condition
xpath: ./Description/Condition
EOF
python src/update_from_csv.py $INPUTDIR/$INXML \
                              --outfile $OUTXML \
                              --deltafile $DELTAXML \
                              --cfgfile tmp/update.yml \
                              --mapfile tmp/$SCRIPT.csv -v 1
bin/syncdelta.sh
bin/syncupdate.sh
