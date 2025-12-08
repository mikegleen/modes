#!/bin/zsh
#
#   Add simple name elements to all records.
#
set -e
start=`date +%s.%N`
INXML=prod_update/normal/2025-12-04_brackets.xml
#
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
echo SCRIPT: $SCRIPT
OUTXML=prod_update/normal/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
#
python src/once/x069_simple_name.py $INXML $OUTXML
python src/xmldiff.py $INXML $OUTXML -o $DELTAXML
#
bin/syncupdate.sh
bin/syncdelta.sh
end=`date +%s.%N`
BC_ENV_ARGS="-e scale=3"
runtime=$( echo "($end - $start)/1.000" | bc )
echo runtime: $runtime seconds

