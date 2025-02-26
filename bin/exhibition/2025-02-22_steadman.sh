#!/bin/zsh
INXML=2025-02-21_del_jb1112.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
# echo $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
SERIAL=LDHRM.2024.33
EXHIBITION=39
STARTDATE=15.2.2025
LOCATION="Joan Brinsmead Gallery"
#
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
                            -o tmp/normal/exhibition.xml \
                            -j $SERIAL -e $EXHIBITION -a \
                            -v 1
#
python src/location.py      update -i tmp/normal/exhibition.xml \
                            -o prod_update/normal/$OUTXML \
                            -a -l $LOCATION -c \
                            -d $STARTDATE \
                            -j $SERIAL -v 1
#
python src/location.py      update -i tmp/normal/exhibition.xml \
                            -o prod_delta/normal/$DELTAXML \
                            -l $LOCATION -c \
                            -d $STARTDATE \
                            -j $SERIAL -v 1
#
bin/syncupdate.sh
bin/syncdelta.sh
