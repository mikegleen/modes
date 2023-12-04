#!/bin/zsh
set -e
INXML=2023-12-03_merged_JB1068.xml
OUTXML=2023-12-03a_denis.xml
cat >tmp/select.yml <<EOF
cmd: ifeq
xpath: ./Acquisition/Person[Role="acquired from"]/PersonName
value: Denis Brinsmead
EOF
cat >tmp/update.yml <<EOF
cmd: constant
xpath: ./Acquisition/Person[Role="acquired from"]/PersonName
value: Brinsmead, Denis
EOF
python src/xml2csv.py prod_update/normal/$INXML tmp/map.csv -c tmp/select.yml --heading
python src/update_from_csv.py prod_update/normal/$INXML prod_update/normal/$OUTXML \
                      -c tmp/update.yml -m tmp/map.csv -a -v 1
bin/syncprod.sh
