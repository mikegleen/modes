#!/bin/zsh
#
INXML=$1
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
