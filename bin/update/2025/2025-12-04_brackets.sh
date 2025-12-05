#!/bin/zsh
#
#   Remove brackets from around dates
#
set -e
INXML=prod_update/normal/2025-11-08_move2jbg.xml
#
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
echo SCRIPT: $SCRIPT
OUTXML=prod_update/normal/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
#
python src/once/x068_brackets.py $INXML $OUTXML
python src/xmldiff.py $INXML $OUTXML -o $DELTAXML
#
bin/syncupdate.sh
bin/syncdelta.sh
