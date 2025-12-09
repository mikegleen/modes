#!/bin/zsh
#
#   Add ExhibitionNumber subelements
#
set -e
start=`date +%s.%N`
INXML=prod_update/normal/2025-12-08_numberofitems.xml
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
echo SCRIPT: $SCRIPT
OUTXML=prod_update/normal/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
#
python src/once/x071_exhibition_number.py $INXML $OUTXML
bin/syncupdate.sh
python src/xmldiff.py $INXML $OUTXML -o $DELTAXML
bin/syncdelta.sh
end=`date +%s.%N`
runtime=$( echo "($end - $start)/1.000" | bc )
echo End ${SCRIPT}. Elapsed: $runtime seconds
