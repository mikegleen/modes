#!/bin/zsh
INXML=2023-07-15_medium.xml
INCSV=../collection/etc/batch021/2023-07-16_batch021_edited.csv
OUTXML=2023-07-22_letters.xml
# cat >tmp/update.csv <<EOF
# EOF
cp ../collection/etc/batch021/2023-07-16_batch021_edited.csv tmp/update.csv
cat >tmp/update.yml <<EOF
cmd: column
xpath: ./Identification/Title
---
cmd: column
xpath: ./Description/Material[Part="medium"]/Keyword
title: Medium
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
xpath: ./Identification/Type
parent_path: ./Identification
---
cmd: column
xpath: ./References/Reference[@elementtype="First Published In"]/Title
title: FirstPublished
---
cmd: column
xpath: ./References/Reference[@elementtype="First Published In"]/Date
title: FirstPublishedDate
---
EOF
python src/update_from_csv.py prod_update/normal/$INXML \
                              prod_update/normal/$OUTXML \
                              -c tmp/update.yml -m $INCSV -r -a -v 2
bin/syncprod.sh
