#!/bin/zsh
set -e
# Modify the following two lines
INXML=2024-04-07_JB119.xml
HEADER='Stocktake 2024'
# -------------------------
cat >tmp/stocktake.yml <<EOF
cmd: column
xpath: ./ObjectLocation[@elementtype="current location"]/Location
title: Current
---
cmd: column
xpath: ./ObjectLocation[@elementtype="normal location"]/Location
title: Normal
---
cmd: column
xpath: ./Identification/Title
width: 100
---
cmd: column
xpath: ./Identification/BriefDescription
title: Description
width: 100
---
cmd: column
xpath: ./Description/Condition/Note
title: Condition
EOF
python src/xml2csv.py prod_update/normal/$INXML tmp/stocktake.csv -c tmp/stocktake.yml --heading
python src/stocktake2docx.py tmp/stocktake.csv 'tmp/stocktake3.docx' --header \"$HEADER\"
