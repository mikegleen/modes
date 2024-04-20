#!/bin/zsh
#
#   Set "display order" aspect values of 9 to all objects.
#
INXML=prod_update/normal/2023-10-14_batch021_type.xml
OUTXML=prod_update/normal/2023-11-07_display_order.xml
cat >tmp/update.yml <<EOF
cmd: constant
aspect: display order
xpath: ./Description
value: 9
EOF
#
# Create mapfile with all accession numbers
#
python src/xml2csv.py $INXML tmp/mapfile.csv --heading
#
# Apply the update
#
python src/update_from_csv.py $INXML $OUTXML -c tmp/update.yml -m tmp/mapfile.csv  -v 1
#
# Test column updates
#
cat >tmp/update2.yml <<EOF
cmd: column
aspect: display order
xpath: ./Description
title: Order
EOF
cat >tmp/mapfile2.csv <<EOF
Serial,Order
JB001,3
EOF
python src/update_from_csv.py $OUTXML tmp/order.xml -c tmp/update2.yml -m tmp/mapfile2.csv -v 1 -r
bin/syncprod.sh
