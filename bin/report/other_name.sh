#!/bin/zsh
#
#
set -e
INCLUDE_FILE=data/vanessa/letter_template_for_update_20250724_G17.xlsx
INXML=prod_update/normal/2025-07-27_objectname.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
STEPHENSXML=tmp/normal/${SCRIPT}_stephens.xml
OUTXML=prod_update/normal/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
#
cat >tmp/update.yml <<EOF
cmd: ifelt
xpath: ./Identification/ObjectName[@elementtype="other name"]
---
column: Type
xpath: ./Identification/Type
---
cmd: attrib
attribute: elementtype
xpath: .
title: ElementType
---
cmd: attrib
attribute: elementtype
title: ObjectName1
xpath: ./Identification/ObjectName[1]
---
column: First Name
xpath: ./Identification/ObjectName[1]/Keyword
---
cmd: attrib
attribute: elementtype
title: ObjectName2
xpath: ./Identification/ObjectName[2]
---
column: Second Name
xpath: ./Identification/ObjectName[2]/Keyword
---
cmd: column
xpath: ./Identification/Title
---
column: Description
xpath: ./Identification/BriefDescription
EOF
python src/xml2csv.py $INXML results/reports/${SCRIPT}.csv -c tmp/update.yml --heading --bom
#
