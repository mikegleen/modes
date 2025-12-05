#!/bin/zsh
#
#   Remove brackets from around dates
#
set -e
INXML=prod_update/pretty/2025-11-08_move2jbg_pretty.xml
#
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
echo SCRIPT: $SCRIPT
OUTXML=prod_update/pretty/$SCRIPT_pretty.xml
DELTAXML=${SCRIPT}_delta.xml
#
python src/once/x068_brackets.py $INXML tmp/normal/${SCRIPT}_step1.xml

#
bin/synctmp.sh
rm tmp/normal/${SCRIPT}_step1.xml
bin/synctmp.sh
# bin/syncupdate.sh
# bin/syncdelta.sh
