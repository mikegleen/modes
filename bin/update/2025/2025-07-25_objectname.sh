#!/bin/zsh
#
#
set -e
INCLUDE_FILE=data/vanessa/letter_template_for_update_20250724_G17.xlsx
INXML=prod_update/normal/2025-06-05_road_show.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
STEPHENSXML=tmp/normal/${SCRIPT}_stephens.xml
OUTXML=prod_update/normal/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
#
# The following commented-out code was used to investigate the XML file before
# applying the update.
#
# cat >tmp/update.yml <<EOF
# column: Type
# xpath: ./Identification/Type
# ---
# cmd: attrib
# attribute: elementtype
# xpath: .
# title: ElementType
# ---
# cmd: attrib
# attribute: elementtype
# title: ObjectName1
# xpath: ./Identification/ObjectName[1]
# ---
# column: First Name
# xpath: ./Identification/ObjectName[1]/Keyword
# ---
# cmd: attrib
# attribute: elementtype
# title: ObjectName2
# xpath: ./Identification/ObjectName[2]
# ---
# column: Second Name
# xpath: ./Identification/ObjectName[2]/Keyword
# ---
# column: Description
# xpath: ./Identification/BriefDescription
# EOF
# python src/xml2csv.py $INXML results/reports/${SCRIPT}_02.csv -c tmp/update.yml --heading
#
cat >tmp/update.yml <<EOF
cmd: delete
parent_path: ./Identification
xpath: ./Identification/Type
---
cmd: constant
parent_path: ./Identification
xpath: ./Identification/ObjectName
attribute: elementtype
attribute_value: simple name
value:
---
column: ObjectName (simple name)
xpath: ./Identification/ObjectName[@elementtype="simple name"]/Keyword
parent_path: ./Identification/ObjectName[@elementtype="simple name"]
EOF
python src/update_from_csv.py $INXML --outfile $OUTXML --deltafile $DELTAXML --cfgfile tmp/update.yml --mapfile $INCLUDE_FILE
bin/syncupdate.sh
bin/syncdelta.sh
