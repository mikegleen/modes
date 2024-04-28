#!/bin/zsh
INXML=2024-04-07_JB119.xml
OUTXML=2024-04-07_magazine.xml
set -e
python src/exhibition.py    prod_update/normal/$INXML \
                            tmp/normal/exhibition.xml \
                            --col_acc b --col_cat a -s 1 -e 35 -a \
                            -m results/csv/exhibitions/2024-03-25_magazine.csv -v 1

#
python src/location.py      update -i tmp/normal/exhibition.xml \
                            -o prod_update/normal/$OUTXML \
                            --col_acc b -s 1 -a -l HRM -c \
                            -d 30.3.2024 \
                            -m results/csv/exhibitions/2024-03-25_magazine.csv -v 1
#bin/syncprod.sh
