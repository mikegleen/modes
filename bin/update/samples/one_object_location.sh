#!/bin/zsh
#
#   Set LDHRM.2023.19 to 'Out for restoration'
#
set -e
INXML=2025-02-23_nocontent
OUTXML=2025-02-28_test
OBJECT=LDHRM.2023.19
LOCATION='Another Location'
#
source bin/boilerplate.sh
#
yellow ----------------------------------------------------
yellow "Update the single object"
yellow ----------------------------------------------------
#
python src/location.py update -i prod_update/normal/${INXML}.xml -o prod_update/normal/${OUTXML}.xml -a \
                        --object $OBJECT --current --location $LOCATION
#
python src/location.py update -i prod_update/normal/${INXML}.xml -o prod_delta/normal/${OUTXML}_delta.xml \
                        -j $OBJECT -c -l $LOCATION
#
bin/syncupdate.sh
bin/syncdelta.sh
