#
#   Correct the dates for some of the nursery pottery.
#
cat >tmp/cfg.yml <<EOF
cmd: column
xpath: ./Production/Date/DateBegin
title: Production DateBegin
---
cmd: constant
xpath: ./Production/Date/Accuracy
title: Production Accuracy
value:
EOF
python src/update_from_csv.py \
 prod_update/normal/2022-04-07_to-day.xml \
 prod_update/normal/2022-04-10_pottery.xml \
 -c tmp/cfg.yml \
 -m data/csv/2022-04-09_decorative3.csv \
 -a -e -v 2
bin/pretty prod_update/normal/2022-04-10_pottery.xml
rm tmp/cfg.yml
