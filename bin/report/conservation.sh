#!/bin/zsh
#
INXML=/Users/mlg/pyprj/hrm/modes/prod_update/normal/2025-09-13a_conservation.xml
DATE=$(date -I)
cat >tmp/group.yml <<EOF
cmd: if
xpath: ./Conservation
group:
---
cmd: column
xpath: ./Conservation/Type
---
cmd: column
xpath: ./Conservation/Person
---
cmd: column
xpath: ./Conservation/Date
group: "|"
---
cmd: column
xpath: ./Conservation/Reason
---
cmd: column
xpath: ./Conservation/SummaryText
---
cmd: column
xpath: ./Conservation
group: "|"
title: Element Group
---
EOF
python src/xml2csv.py $INXML results/reports/${DATE}_conservation.csv -b -c tmp/group.yml --heading
