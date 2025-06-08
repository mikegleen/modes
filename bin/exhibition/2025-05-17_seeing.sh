#!/bin/zsh
INXML=
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
# echo $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
EXHIBITION=40
#
cat >tmp/$SCRIPT.csv <<EOF
Serial
SH41
JB379
JB105
EOF
set -e
python src/exhibition.py    prod_update/normal/$INXML \
                            --mapfile tmp/$SCRIPT.csv \
                            --outfile prod_update/normal/$SCRIPT.xml \
                            --deltafile prod_delta/normal/${SCRIPT}_delta.xml \
                            --exhibition $EXHIBITION \
                            --move_to_location \
                            --verbose 1
#
bin/syncupdate.sh
bin/syncdelta.sh
