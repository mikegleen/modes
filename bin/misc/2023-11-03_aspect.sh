#!/bin/zsh
set -e
OUTXML=2023-10-14_batch021_type.xml
cat >tmp/update.yml <<EOF
cmd: ifattribnoteq
xpath: .
attribute: elementtype
value: Original Artwork
---
# cmd: column
# xpath: ./Identification/Title
# title: Title
# ---
cmd: attrib
xpath: .
attribute: elementtype
---
cmd: column
xpath: ./Identification/ObjectName[@elementtype="simple name"]/Keyword
title: Simple Name
---
cmd: column
xpath: ./Identification/ObjectName[@elementtype="other name"]/Keyword
title: Other Name
---
EOF
python src/xml2csv.py prod_update/normal/$OUTXML tmp/objectname.csv --heading -c tmp/update.yml -b
