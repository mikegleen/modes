#!/bin/zsh
#
#   Copied from: bin/make/2024-07-04_postcards.sh
#
set -e
INXML=2025-02-07_stocktake_loc_pretty.xml
OUTXML=2025-02-17_postcards.xml
DELTAXML=2025-02-17_postcards_delta.xml
#
# Step 2. Add the six postcards as Item elements
#
cat >tmp/in2.csv <<EOF
Serial,Subid,Title
2024.24,1,The Gadgets
2024.24,2,The Kitchen
2024.24,3,The Dining Room
2024.24,4,The Nursery
2024.24,5,The Bedroom
2024.24,6,The Garden
EOF
cat >tmp/update2.yml <<EOF
cmd: global
add_mda_code:
subid_grandparent: .
subid_parent: ItemList
---
cmd: subid
title: Subid
---
cmd: column
xpath: Title
EOF
python src/update_from_csv.py prod_update/normal/$INXML prod_update/normal/$OUTXML -c tmp/update2.yml -m tmp/in2.csv -v 1 -a
python src/update_from_csv.py prod_update/normal/$INXML prod_delta/normal/$DELTAXML -c tmp/update2.yml -m tmp/in2.csv -v 1
bin/syncprod.sh
bin/syncdelta.sh
