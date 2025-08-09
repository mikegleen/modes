#!/bin/zsh
set -e
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
INCSV=tmp/update.csv
#
# Input XML file containing the full database in prod_update/normal/
INXML=2025-08-07_prod_save_sorted.xml
#
# Directory definitions
#
INPUTDIR=prod_update/normal
NEWOBJDIR=prod_make/normal
OUTPUTDIR=prod_update/normal
#
# Output XML file containing the new Object records in prod_make/normal/
NEWXML=$NEWOBJDIR/$SCRIPT.xml
#
# Output XML file containing the merged and sorted new full database in prod_update/normal
MERGEDXML=$SCRIPT.xml
#
#
#
cat >tmp/update.csv <<EOF
Serial,Location,HxW,Title
JB1105.1,G7,190x145 mm,Testing Golf Drivers
JB1105.2,G7,190x145 mm,Anti-Litter Machine
JB1105.3,G7,190x145 mm,How to Build a Bungalow
JB1105.4,G7,190x145 mm,Altering the Time on Big Ben
JB1105.5,G7,190x145 mm,A Leak in the Channel Tunnel
EOF
cat >tmp/update.yml <<EOF
# For new JB1105 sub-objects
column: Location
xpath: ./ObjectLocation[@elementtype="current location"]/Location
xpath2: ./ObjectLocation[@elementtype="normal location"]/Location
---
column: HxW
xpath: ./Description/Measurement/Reading
---
column: Title
xpath: ./Identification/Title
---
cmd: constant
xpath: ./ObjectLocation[@elementtype="current location"]/Date/DateBegin
value: "21.2.2019"
---
cmd: reproduction
xpath: ./Reproduction/Filename
EOF
python src/csv2xml.py -o $NEWXML \
                      --cfgfile tmp/update.yml \
                      --incsvfile $INCSV \
                      --template templates/normal/ephemera_item_template.xml \
                      -v 1
bin/syncmake.sh
python src/merge_xml.py -i $INPUTDIR/$INXML -i $NEWXML -o tmp/$MERGEDXML -v 1
python src/sort_xml.py tmp/$MERGEDXML $OUTPUTDIR/$MERGEDXML -v 1
bin/syncupdate.sh
