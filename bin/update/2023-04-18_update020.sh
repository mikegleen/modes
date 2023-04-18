cat >tmp/update.csv <<EOF
Serial,Date,Accuracy
JB608-9,1930,circa
EOF
cat >tmp/update.yml <<EOF
cmd: column
xpath: ./Production/Date/DateBegin
parent_path: ./Production/Date
title: Date
---
cmd: column
xpath: ./Production/Date/Accuracy
parent_path: ./Production/Date
title: Accuracy
---
EOF
python src/update_from_csv.py prod_update/normal/2023-04-08a_measurement.xml \
                              prod_update/normal/2023-04-18_batch020.xml \
                              -c tmp/update.yml -m tmp/update.csv \
                              -a
