#!/bin/zsh
#
#
set -e
INCLUDE_FILE=data/vanessa/letter_template_for_update_20250724_G17.xlsx
# INCLUDE_FILE=tmp/include.csv
INXML=prod_update/normal/2025-06-05_road_show.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
STEPHENSXML=tmp/normal/${SCRIPT}_stephens.xml
OUTXML=prod_update/normal/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
cat >tmp/include.csv <<EOF
Serial,ObjectName (simple name),BriefDescription
SH106,illustration,illustration attached to one card board
EOF
cat >tmp/update.yml <<EOF
cmd: delete
parent_path: ./Identification
xpath: ./Identification/Type
---
cmd: constant
parent_path: ./Identification
xpath: ./Identification/ObjectName[@elementtype="simple name"]
attribute: elementtype
attribute_value: simple name
value:
---
column: ObjectName (simple name)
xpath: ./Identification/ObjectName[@elementtype="simple name"]/Keyword
parent_path: ./Identification/ObjectName[@elementtype="simple name"]
---
column: BriefDescription
xpath: ./Identification/BriefDescription
EOF
python src/update_from_csv.py $INXML --outfile $OUTXML --deltafile $DELTAXML --cfgfile tmp/update.yml --mapfile $INCLUDE_FILE
bin/syncupdate.sh
bin/syncdelta.sh
