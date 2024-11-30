#!/bin/zsh
INXML=2024-10-25_merged_batch026_accessions.xml
OUTXML=2024-11-15_stormp.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: constant
xpath: ./Description/Aspect[Keyword="display order"]/Reading
value: 6
EOF
cat >tmp/$SCRIPT.csv <<EOF
Serial
LDHRM.2021.12
EOF
set -e
python src/exhibition.py    prod_update/normal/$INXML \
                            -o tmp/normal/$SCRIPT.xml \
                            -j LDHRM.2021.12 -e 38 -a \
                            -v 1
#
python src/update_from_csv.py tmp/normal/$SCRIPT.xml \
                              prod_delta/normal/$OUTXML \
                              -c tmp/$SCRIPT.yml  \
                              -m tmp/$SCRIPT.csv -v 3
#
python src/update_from_csv.py tmp/normal/$SCRIPT.xml \
                              prod_update/normal/$OUTXML \
                              -c tmp/$SCRIPT.yml -a \
                              -m tmp/$SCRIPT.csv -v 1
#
bin/syncupdate.sh
bin/syncdelta.sh
