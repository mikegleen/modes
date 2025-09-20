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
COMMON_ARGS=--object $OBJECT --current --location $LOCATION
#
yellow ----------------------------------------------------
yellow "Update the single object"
yellow ----------------------------------------------------
#
python src/location.py update -i prod_update/normal/${INXML}.xml -o prod_update/normal/${OUTXML}.xml -a \
                        $COMMON_ARGS
#
python src/location.py update -i prod_update/normal/${INXML}.xml -o prod_delta/normal/${OUTXML}_delta.xml \
                        $COMMON_ARGS
#
bin/syncupdate.sh
bin/syncdelta.sh
