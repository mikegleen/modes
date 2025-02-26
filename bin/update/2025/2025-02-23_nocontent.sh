#!/bin/zsh
#
#   Move the data from fields under <Content>
#
set -e
INXML=2025-02-22_steadman.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
# Step 1.
#
cat >tmp/in2.csv <<EOF
Serial,BriefDescription,Notes,RelatedObject
JB1121,"Includes in the sale “A Portrait of my Father” by Oliver Robinson, and a WHR original donated by Oliver Robinson and Joan Brinsmead"
LDHRM.2022.5,"Illustrated books and related drawings. Knightsbridge: Bonhams &amp; Brooks, 2001. HRMT purchased Fireside Futurism (JB623) and Good Night Everybody (JB624) from this sale."
LDHRM.2022.6,,WHR’s son Alan was a monk at Prinknash Abbey. WHR gave the monks this cartoon as they built their new abbey in the grounds of their original small building.,JB1101
LDHRM.2022.7,,WHR’s son Alan was a monk at Prinknash Abbey. WHR gave the monks this cartoon as they built their new abbey in the grounds of their original small building.,JB1101
EOF
cat >tmp/update2.yml <<EOF
cmd: column
xpath: ./Identification/BriefDescription
---
cmd: column
xpath: ./Notes
---
cmd: constant
xpath: ./RelatedObject[@elementtype="duplicates"]
parent_path: .
attribute: elementtype
attribute_value: duplicates
if_other_column: RelatedObject
value:
---
cmd: constant
xpath: ./RelatedObject/ObjectIdentity
parent_path: ./RelatedObject
value:
if_other_column: RelatedObject
---
cmd: column
xpath: ./RelatedObject/ObjectIdentity/Number
parent_path: ./RelatedObject/ObjectIdentity
title: RelatedObject
---
EOF
#
#   Step 2. Select objects with a Content element group.
#
python src/update_from_csv.py prod_update/normal/$INXML tmp/normal/$OUTXML -c tmp/update2.yml -m tmp/in2.csv --replace -v 1 -a
cat >tmp/select.yml <<EOF
cmd: ifelt
xpath: ./Content
EOF
python src/xml2csv.py prod_update/normal/$INXML tmp/serial.csv -c tmp/select.yml --heading
#
#   Step 3. Delete all occurrences of Content elements
#
cat >tmp/update2.yml <<EOF
cmd: delete
xpath: ./Content
parent_path: .
EOF
python src/update_from_csv.py tmp/normal/$OUTXML prod_delta/normal/$DELTAXML  -c tmp/update2.yml -m tmp/serial.csv
python src/update_from_csv.py tmp/normal/$OUTXML prod_update/normal/$OUTXML  -c tmp/update2.yml -m tmp/serial.csv -a
bin/syncupdate.sh
bin/syncdelta.sh
python src/xmldiff.py prod_update/normal/$INXML prod_update/normal/$OUTXML --outorig tmp/normal/before.xml
bin/synctmp.sh
