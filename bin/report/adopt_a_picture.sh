#!/bin/zsh
INXML=/Users/mlg/pyprj/hrm/modes/prod_update/normal/2025-09-13a_conservation.xml
DATE=$(date -I)
cat >tmp/adopt.yml <<EOF
cmd: ifeq
xpath: ./Association/Type
value: Adopt a Picture
---
cmd: column
xpath: ./Identification/Title
---
cmd: column
xpath: ./Association/Person/PersonName
title: Name
---
cmd: column
xpath: ./Association/Date
---
cmd: column
xpath: ./Association/SummaryText/Note
EOF
python src/xml2csv.py $INXML results/reports/${DATE}_adopt.csv -b -c tmp/adopt.yml --heading
