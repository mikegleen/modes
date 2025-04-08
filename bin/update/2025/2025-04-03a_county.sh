#!/bin/zsh
#
#
set -e
INXML=2025-04-03_sh8.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
python src/once/x059_county.py prod_update/normal/$INXML prod_update/normal/$OUTXML
python src/xmldiff.py prod_update/normal/$INXML prod_update/normal/$OUTXML -o prod_delta/normal/$DELTAXML
bin/syncupdate.sh
bin/syncdelta.sh

