#!/bin/zsh
#
#   Fix the problem that JB1048 and JB1112 are duplicate entries.
#
set -e
start=`date +%s.%N`
INXML=2025-02-07_stocktake_loc.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
# Step 1. Delete JB1112
#
cat >tmp/$SCRIPT.csv <<EOF
JB1112
EOF
python src/filter_xml.py prod_update/normal/$INXML tmp/${SCRIPT}_step1.xml \
        --include tmp/$SCRIPT.csv \
        -v 1 -x
#
#   Step 2. Update JB1048
#
cat >tmp/$SCRIPT.csv <<EOF
Serial,BriefDescription,RelatedObject,PersonName,Condition
JB1048,"A letterpress pamphlet plus 6 plates detailing the progression of an illustration ""The Young Pan"" issued in a portfolio. Part 7 in a series of 20 volumes on individual illustrators.",LDHRM.2024.33,Percy Bradshaw,Foxed. First and last pages of text loose.
EOF
cat >tmp/$SCRIPT.yml <<EOF
column: BriefDescription
xpath: ./Identification/BriefDescription
---
cmd: constant
xpath: ./RelatedObject[@elementtype="duplicates"]
parent_path: .
attribute: elementtype
attribute_value: duplicates
value:
---
cmd: constant
xpath: ./RelatedObject/ObjectIdentity
parent_path: ./RelatedObject
value:
---
cmd: column
xpath: ./RelatedObject/ObjectIdentity/Number
parent_path: ./RelatedObject/ObjectIdentity
title: RelatedObject
---
cmd: column
person_name:
xpath: ./Production/Person[Role="author"]/PersonName
---
column: Condition
xpath: ./Description/Condition/Note
EOF
#
# We use --force because we want to replace "Percy Bradshaw" with "Percy Bradshaw"
# but have included the person_name statement so that it is converted to "Bradshaw, Percy".
#
python src/update_from_csv.py tmp/${SCRIPT}_step1.xml tmp/${SCRIPT}_step2.xml \
        -c tmp/$SCRIPT.yml -m tmp/$SCRIPT.csv -v 1 -a --replace --force
python src/update_from_csv.py tmp/${SCRIPT}_step1.xml tmp/${SCRIPT}_step2_delta.xml \
        -c tmp/$SCRIPT.yml -m tmp/$SCRIPT.csv -v 1 --replace --force
#
# Step 3. Create a placeholder version of JB1112
#
cat >tmp/$SCRIPT.csv <<EOF
Serial,Notes
JB1112,This was an accidental duplicate of JB1048.
EOF
cat >tmp/$SCRIPT.yml <<EOF
cmd: column
xpath: ./Notes
EOF
python src/csv2xml.py -i tmp/$SCRIPT.csv -o tmp/${SCRIPT}_step3.xml \
        -c tmp/$SCRIPT.yml -t templates/normal/placeholder_template.xml
#
# Step 4. Merge Step 2 (full file with JB1112 deleted and JB1048 updated) with
#         Step 3, (placeholder JB1112)
python src/merge_xml.py -i tmp/${SCRIPT}_step2.xml -i tmp/${SCRIPT}_step3.xml \
                        -o tmp/${SCRIPT}_step4.xml
python src/sort_xml.py tmp/${SCRIPT}_step4.xml prod_update/normal/${OUTXML}
#
# Step 5. Merge the two objects to create the delta file for Modes.
#
python src/merge_xml.py -i tmp/${SCRIPT}_step2_delta.xml -i tmp/${SCRIPT}_step3.xml \
                        -o  prod_delta/normal/${DELTAXML}
#
rm tmp/${SCRIPT}*
bin/syncupdate.sh
bin/syncdelta.sh
end=`date +%s.%N`
runtime=$( echo "$end - $start" | bc -l )
echo runtime: $runtime seconds
