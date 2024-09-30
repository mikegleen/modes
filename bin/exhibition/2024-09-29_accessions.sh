#!/bin/zsh
INXML=2024-09-28_fix_sizes.xml
OUTXML=2024-09-29_accessions.xml
INCSV=data/acquisitions/2024-09-06/2024-09-18_MergedAccessions.xlsx
set -e
python src/exhibition.py    prod_update/normal/$INXML \
                            -o prod_update/normal/$OUTXML \
                            --col_acc a --col_ex w -s 0 -a \
                            -m $INCSV -v 1 --allow_missing
#
python src/exhibition.py    prod_update/normal/$INXML \
                            -o prod_delta/normal/$OUTXML \
                            --col_acc a --col_ex w -s 0 \
                            -m $INCSV -v 1 --allow_missing
#
bin/syncupdate.sh
bin/syncdelta.sh
