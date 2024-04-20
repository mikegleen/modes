#!/bin/zsh
INXML=2023-09-30d_SH100.xml
INCSV=../collection/etc/batch021/2023-10-07_batch021_edited.xlsx
OUTXML=2023-10-07_batch021_fix.xml
# cat >tmp/update.csv <<EOF
# EOF
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
title: Production Date
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
title: First Published In
---
cmd: column
xpath: ./References/Reference[@elementtype="First Published In"]/Date
title: First Published Date
---
cmd: column
xpath: ./References/Reference[@elementtype="First Published In"]/Page
parent_path: ./References/Reference[@elementtype="First Published In"]
title: First Published Page
---
cmd: column
xpath: ./References/Reference[@elementtype="Reproduced In"]/Title
parent_path: ./References/Reference[@elementtype="Reproduced In"]
title: Reproduced In
---
cmd: column
xpath: ./References/Reference[@elementtype="Reproduced In"]/Page
parent_path: ./References/Reference[@elementtype="Reproduced In"]
title: Reproduced In Page
---
EOF
python src/update_from_csv.py prod_update/normal/$INXML \
                              prod_update/normal/$OUTXML \
                              -c tmp/update.yml -m $INCSV -r -a -v 2
bin/syncprod.sh
