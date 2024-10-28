#!/bin/zsh
#
# Patch badly formated sizes
#
set -e
INXML=prod_update/normal/2024-10-21_edit.xml
OUTFULLXML=prod_update/normal/2024-10-25_fix_sizes.xml
cat >tmp/sizes.csv <<EOF
Serial,Size
JB1213.1,136x214
JB1213.2,271x212
JB1213.3,181x136
JB1213.4,108x131
JB1213.5,131x194
JB1213.6,59x52
JB1213.7,280x209
JB1213.8,279x212
JB1213.9,264x205
JB1213.10,276x215
JB1213.11,265x204
JB1213.12,110x210
JB1213.13,246x189
JB1213.14,220x200
JB1213.15,212x272
JB1213.16,274x189
JB1213.17,276x213
EOF
cat >tmp/config.yml <<EOF
column: Size
xpath: ./Description/Measurement[Part="image"]/Reading
EOF
python src/update_from_csv.py $INXML $OUTFULLXML -a -r -m tmp/sizes.csv -c tmp/config.yml
bin/syncupdate.sh
