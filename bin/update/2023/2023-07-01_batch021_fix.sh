#!/bin/zsh
INXML=2023-05-21_loc.xml
OUTXML=2023-06-12_canprints.xml
cat >tmp/update.csv <<EOF
Serial,Medium,Title,Type,Description,NewDate,Accuracy
JB639,pen and watercolour
SH60,pen and pencil
SH169,pen and pencil
SH172,pen and pencil
SH78,watercolour
SH89,watercolour
SH91,watercolour
EOF
cat >tmp/update.yml <<EOF
cmd: column
xpath: ./Identification/Title
---
cmd: column
xpath: ./Identification/Type
parent_path: ./Identification
---
cmd: column
xpath: ./Identification/BriefDescription
title: Description
---
cmd: column
xpath: ./Production/Date/DateBegin
title: NewDate
---
cmd: column
xpath: ./Production/Date/Accuracy
parent_path: ./Production/Date
---
cmd: column
xpath: ./Description/Material[Part="medium"]/Keyword
title: Medium
---
EOF
python src/update_from_csv.py prod_update/normal/$INXML \
                              prod_update/normal/$OUTXML \
                              -c tmp/update.yml -m tmp/update.csv -r -a -v 2
bin/syncprod.sh
