# Remove "To-day" as first published
#
cat >tmp/cfg.yml <<EOF
cmd: constant
xpath: ./References/Reference[@elementtype="First Published In"]/Date
value:
---
cmd: constant
xpath: ./References/Reference[@elementtype="First Published In"]/Title
value:
---
EOF
python src/update_from_csv.py prod_update/normal/2022-04-10_pottery.xml \
 prod_update/normal/2022-04-11_clear_to-day.xml \
 -c tmp/cfg.yml \
 -m data/csv/2022-04-11_today.csv \
 -e -v 2 -a
#
cat >tmp/cfg.yml <<EOF
cmd: constant
xpath: ./Production/Date/Accuracy
parent_path: ./Production/Date
value: circa
---
cmd: constant
xpath: ./Production/Date/DateBegin
value: '1935'
---
EOF
cat >tmp/map.csv <<EOF
LDHRM.2019.29
EOF
python src/update_from_csv.py prod_update/normal/2022-04-11_clear_to-day.xml \
 prod_update/normal/2022-04-11_set_circa.xml \
 -c tmp/cfg.yml \
 -m tmp/map.csv \
 -e -v 2 -a
bin/pretty prod_update/normal/2022-04-11_set_circa.xml
