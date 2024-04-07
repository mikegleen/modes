#!/bin/zsh
cat >tmp/adopt.yml <<EOF
cmd: ifeq
xpath: ./Association/Type
value: Adopt a Picture
---
cmd: column
xpath: ./Identification/Title
---
cmd: column
xpath: ./Association/Person/Name
---
cmd: column
xpath: ./Association/Date
---
cmd: column
xpath: ./Association/SummaryText/Note
EOF
python src/xml2csv.py prod_update/pretty/2023-12-11a_del_previous_pretty.xml results/reports/adopt.csv -b -c tmp/adopt.yml --heading
