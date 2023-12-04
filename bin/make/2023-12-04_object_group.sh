#!/bin/zsh
set -e
INCSV=../letters/from_geoffrey/LETTERS1.csv
INXML=2023-12-04_renumber.xml
OUTXML=2023-12-04a_object_group.xml
MERGEDXML=2023-12-04a_merged.xml
cat >tmp/update.yml <<EOF
cmd: column
xpath: ./Identification/BriefDescription
title: Description
---
cmd: column
xpath: ./ObjectLocation[@elementtype="current location"]/Location
title: Location
---
cmd: constant
xpath: ./ObjectLocation[@elementtype="current location"]/Date/DateBegin
title: Location Date
value: 24.11.2023
---
EOF
python src/csv2xml.py -o prod_make/normal/$OUTXML \
                      -c tmp/update.yml -i $INCSV -v 1 -t etc/templates/normal/2023-11-24_object_group_template.xml
bin/syncmake.sh
python src/merge_xml.py prod_update/normal/$INXML prod_make/normal/$OUTXML tmp/merged.xml -v 1
python src/sort_xml.py tmp/merged.xml prod_update/normal/$MERGEDXML -v 1
bin/syncprod.sh
