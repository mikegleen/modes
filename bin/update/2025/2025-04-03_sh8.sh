#!/bin/zsh
set -e
#
#   Apply the update to SH8 and JB1142 (2nd update) downloaded from Modes
#
# SCRIPT is the script name without the path and trailing ".sh"
SCRIPT=${ZSH_ARGZERO:t:r}
echo SCRIPT: $SCRIPT
#
# SAVEDIR is the directory we downloaded the updated XML to from Modes.
# INXML master file from prod_update/normal
# INDETAIL detail file containing merged files from prod_save/normal downloaded from Modes
SAVEDIR=prod_save/normal
INXML=2025-03-30_patch_place.xml
INDETAIL=tmp/${SCRIPT}_sorted.xml
python src/merge_xml.py  --infile $SAVEDIR/2025-04-03_sh8.xml --infile $SAVEDIR/2025-04-05_JB1142.xml --outfile tmp/${SCRIPT}_merged.xml
python src/sort_xml.py tmp/${SCRIPT}_merged.xml $INDETAIL
#
OUTXML=$SCRIPT.xml
#
python src/xmlupd.py prod_update/normal/$INXML $INDETAIL --outfile prod_update/normal/$OUTXML
bin/syncupdate.sh
