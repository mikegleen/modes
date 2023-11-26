#!/bin/zsh
set -e
cat >tmp/update.yml <<EOF
cmd: ifelt
xpath: ./Association[Type="Adopt a Picture"]
---
cmd: column
xpath: ./Association[Type="Adopt a Picture"]/Person/Name
EOF
python src/xml2csv.py /Users/mlg/pyprj/hrm/modes/prod_update/normal/2023-11-20_merged.xml tmp/adopt.csv --heading -c tmp/update.yml
