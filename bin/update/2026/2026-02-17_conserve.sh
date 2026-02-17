#!/bin/zsh
#
#   Move page numbers from Aspect.text to Aspect/Reading.text
#
set -e
INXML=prod_save/normal/2026-02-17_prod_save_sorted.xml
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
MAPCSV=tmp/$SCRIPT.csv
cat >tmp/$SCRIPT.csv <<EOF
Serial
2023.16-19
EOF
cat >tmp/$SCRIPT.yml <<EOF
cmd: constant
xpath: ./Conservation/Person/Role
parent_path: ./Conservation/Person
value: conservator
---
cmd: constant
xpath: ./Conservation/Person/PersonName
parent_path: ./Conservation/Person
value: Bates, Deborah
---
cmd: constant
xpath: ./Conservation/Date
value: 2025
EOF
#
#
python src/update_from_csv.py $INXML --outfile prod_update/normal/$SCRIPT.xml \
                                     --deltafile prod_delta/normal/${SCRIPT}_delta.xml \
                                     --cfgfile tmp/${SCRIPT}.yml \
                                     --mapfile $MAPCSV \
                                     --replace
bin/syncupdate.sh
bin/syncdelta.sh
