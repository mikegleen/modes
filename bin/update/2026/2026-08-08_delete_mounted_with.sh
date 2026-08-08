#!/bin/zsh
set -e
INXML=prod_save/normal/2026-08-08_prod_save_sorted.xml
INXML=$(python src/utl/x066_latest.py -i prod_save/normal)
SCRIPT="$(basename -- "${0%.*}")"
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: ifnot
xpath: ./RelatedObject[@elementtype="Mounted With"]/ObjectIdentity/Number
title: if_mounted_with
---
cmd: delete
parent_path: ./RelatedObject[@elementtype="Mounted With"]
xpath: ./RelatedObject[@elementtype="Mounted With"]/ObjectIdentity
---
EOF
# python src/xml2csv.py $INXML tmp/mapfile.csv
# python src/update_from_csv.py $INXML -o tmp/normal/$SCRIPT.xml -c tmp/$SCRIPT.yml -m tmp/mapfile.csv
python src/update_from_csv.py $INXML -o tmp/normal/$SCRIPT.xml -c tmp/$SCRIPT.yml -m all
bin/synctmp.sh
