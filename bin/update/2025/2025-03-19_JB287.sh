#!/bin/zsh
#
#   Apply the update to JB287 downloaded from Modes
#
set -e
INXML=2025-03-14_location.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('/')[-1].split('.')[0])")
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
#python src/xmlupd.py prod_update/normal/$INXML prod_save/normal/2025-03-19_JB287.xml -o prod_update/normal/${SCRIPT}.xml
python src/xmlupd.py prod_update/normal/$INXML prod_save/normal/2025-03-19_JB287.xml -o tmp/normal/${SCRIPT}.xml
