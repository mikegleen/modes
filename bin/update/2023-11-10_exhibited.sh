#!/bin/zsh
#
cat >tmp/cfg.yml <<EOF
cmd: if
xpath: ./Exhibition/ExhibitionName
---
cmd: global
skip_number:
---
cmd: column
normalize:
xpath: ./ObjectIdentity/Number
EOF
python src/xml2csv.py prod_update/pretty/2023-11-07_display_order_pretty.xml tmp/exhibited.csv -c tmp/cfg.yml
cat >tmp/cfg2.yml <<EOF
cmd: if
xpath: ./Exhibition[Place="Dulwich Picture Gallery"]
---
cmd: global
skip_number:
---
cmd: column
normalize:
xpath: ./ObjectIdentity/Number
EOF
python src/xml2csv.py prod_update/pretty/2023-11-07_display_order_pretty.xml tmp/dulwich.csv -c tmp/cfg2.yml
awk '{sub("\r$", ""); print $1 ",3"}' tmp/dulwich.csv >tmp/dulwich2.csv
comm -2 -3  tmp/exhibited.csv tmp/dulwich.csv >tmp/not_dulwich.csv
awk '{sub("\r$", ""); print $1 ",6"}' tmp/not_dulwich.csv >tmp/not_dulwich2.csv
cat tmp/dulwich2.csv tmp/not_dulwich2.csv | awk 'BEGIN {print "Serial,Order"}{print}' > tmp/update_order.csv
#
cat >tmp/cfg3.yml <<EOF
cmd: column
aspect: display order
xpath: ./Description
title: Order
EOF
python src/update_from_csv.py prod_update/normal/2023-11-07_display_order.xml prod_delta/normal/2023-11-09_display_order.xml -m tmp/update_order.csv -c tmp/cfg3.yml -r
