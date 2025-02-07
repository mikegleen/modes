#!/bin/zsh
#
# Patch badly formated sizes
#
set -e
INXML=prod_update/normal/2024-09-23_part_image.xml
OUTFULLXML=prod_update/normal/2024-09-28_fix_sizes.xml
cat >tmp/sizes.csv <<EOF
Serial,Size
JB613,140x120mm
JB701,203x315
JB702,203x315
SH201,91x146
EOF
cat >tmp/config.yml <<EOF
column: Size
xpath: ./Description/Measurement[Part="image"]/Reading
EOF
python src/update_from_csv.py $INXML $OUTFULLXML -a -r -m tmp/sizes.csv -c tmp/config.yml
bin/syncupdate.sh
