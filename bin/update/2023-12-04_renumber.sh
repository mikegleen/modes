#!/bin/zsh
set -e
INXML=2023-12-03a_denis.xml
OUTXML=2023-12-04_renumber.xml
cat >tmp/renum.csv <<EOF
OldSerial,NewSerial
JB1226,JB1069
JB1227,JB1070
EOF
python src/sort_xml.py prod_update/normal/$INXML prod_update/normal/$OUTXML -r tmp/renum.csv
bin/syncprod.sh
