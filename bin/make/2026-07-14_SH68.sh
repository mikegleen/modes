#!/bin/zsh
set -e
INCSV=tmp/update.csv
#
# Input XML file containing the full database in prod_update/normal/
INXML=/Users/mlg/pyprj/hrm/modes/prod_save/normal/2026-07-13s_prod_save_sorted.xml
#
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('/')[-1].split('.')[0])")
echo SCRIPT: $SCRIPT
# Output XML file containing the new Object records in prod_make/normal/
OUTXML=${SCRIPT}.xml
#
# Output XML file containing the merged and sorted new full database in prod_update/normal
MERGEDXML=${SCRIPT}_merged.xml
cat >tmp/update.csv <<EOF
Serial
SH68.1
SH68.2
SH68.3
SH68.4
SH68.5
SH68.6
SH68.7
SH68.8
SH68.9
SH68.10
SH68.11
SH68.12
SH68.13
SH68.14
SH68.15
SH68.16
SH68.17
SH68.18
SH68.19
SH68.20
SH68.21
SH68.22
SH68.23
SH68.24
SH68.25
SH68.26
SH68.27
SH68.28
SH68.29
SH68.30
SH68.31
SH68.32
EOF
#
cat >tmp/update.yml <<EOF
cmd: global
serial: Serial
template_file: /Users/mlg/pyprj/hrm/modes/templates/normal/Original_Artwork_template.xml
---
cmd: constant
xpath: ./Identification/Title
value: Mr Spodnoodle comic strip
---
cmd: constant
xpath: ./Production/Person[Role="artist"]/PersonName
value: Heath Robinson, William
---
cmd: constant
xpath: ./Identification/BriefDescription
value: See SH68 for details
---
cmd: constant
title: Size mm HxW
xpath: ./Description/Measurement[Part="image"]/Reading
value: 125x580
---
cmd: constant
title: Location
xpath: ./ObjectLocation[@elementtype="current location"]/Location
xpath2: ./ObjectLocation[@elementtype="normal location"]/Location
value: BB1
---
cmd: constant
title: Location datebegin
xpath: ./ObjectLocation[@elementtype="current location"]/Date/DateBegin
value: 13.4.2015
---
cmd: reproduction
xpath: ./Reproduction/Filename
EOF
python src/csv2xml.py -o prod_make/normal/$OUTXML \
                      -c tmp/update.yml \
                      -i $INCSV \
                      -v 1
bin/syncmake.sh
#
python src/mergexml.py $INXML prod_make/normal/$OUTXML -o prod_update/normal/$MERGEDXML -v 1
bin/syncupdate.sh
