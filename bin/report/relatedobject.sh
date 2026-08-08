#!/bin/zsh
set -e
INXML=`python src/utl/x066_latest.py -i prod_update/normal`
SCRIPT="$(basename -- "${0%.*}")"
OUTCSV=tmp/$SCRIPT.csv
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: global
# skip_number:
---
cmd: ifnot
xpath: ./RelatedObject[@elementtype="Mounted With"]/ObjectIdentity/Number
title: if_mounted_with
---
cmd: column
xpath: ./RelatedObject[@elementtype="Mounted With"]/ObjectIdentity/Number
---
# cmd: column
# xpath: ./Identification/Title
# width: 50
# ---
EOF
python src/xml2csv.py $INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
