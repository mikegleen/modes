#!/bin/zsh
set -e
#
#   Apply the update to JB1142 downloaded from Modes
#
# INXML master file from prod_update/normal
# INDETAIL detail file from prod_save/normal downloaded from Modes
INXML=2025-03-19_JB287.xml
INDETAIL=2025-03-29_JB1142.xml
#
# SCRIPT is the script name without the path and trailing ".sh"
SCRIPT=${ZSH_ARGZERO:t:r}
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
#
python src/xmlupd.py prod_update/normal/$INXML prod_save/normal/$INDETAIL -o prod_update/normal/$OUTXML
bin/syncupdate.sh
