#!/bin/zsh
INXML=2023-04-21_loc.xml
OUTXML=2023-04-26_measurement.xml
cat >tmp/update.csv <<EOF
Serial,Reading
SH28,390x305mm
EOF
cat >tmp/update.yml <<EOF
cmd: column
xpath: ./Description/Measurement[Part='Image']/Reading
---
EOF
python src/update_from_csv.py prod_update/normal/$INXML \
                              prod_update/normal/$OUTXML \
                              -a -c tmp/update.yml -m tmp/update.csv
INXML=2023-04-26_measurement.xml
OUTXML=2023-04-26_measurement2.xml
cat >tmp/update.csv <<EOF
Serial,Reading
LDHRM.2022.11-22,195x143mm
EOF
cat >tmp/update.yml <<EOF
cmd: constant
xpath: ./Description/Measurement/Part
value: Image
---
cmd: column
xpath: ./Description/Measurement/Reading
---
EOF
python src/update_from_csv.py prod_update/normal/$INXML \
                              prod_update/normal/$OUTXML \
                              -a -c tmp/update.yml -m tmp/update.csv
bin/syncprod.sh
