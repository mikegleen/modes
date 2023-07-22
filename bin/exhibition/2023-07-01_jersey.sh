#!/bin/zsh
set -e
python src/exhibition.py    prod_update/normal/2023-06-23_edit.xml \
                            tmp/normal/2023-07-01_jersey.xml \
                            --col_acc c -s 1 -e 31 -a \
                            -m results/csv/hannah/jersey.csv
#
python src/location.py      update -i tmp/normal/2023-07-01_jersey.xml \
                            -o prod_update/normal/2023-07-01_jersey.xml \
                            --col_acc c -s 1 -a -l 'Jersey Arts Centre' -c \
                            -d 12.6.2023 \
                            -m results/csv/hannah/jersey.csv
bin/syncprod.sh
