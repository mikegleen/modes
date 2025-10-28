#!/bin/zsh
#
INXML=/Users/mlg/pyprj/hrm/modes/test/normal/group.xml
DATE=$(date -I)
cat >tmp/group.yml <<EOF
cmd: if
xpath: ./Production/Date
group:
---
cmd: column
xpath: ./Production/Date
group: '|'
---
EOF
python src/xml2csv.py $INXML test/results/${DATE}_group.csv -b -c tmp/group.yml --heading
