#!/bin/zsh
#
#   Delete unnecessary NumberOfItem elements
#
set -e
start=`date +%s.%N`
INXML=prod_update/normal/2025-12-06a_simple_name.xml
PRETTYINXML=prod_update/pretty/2025-12-06a_simple_name_pretty.xml
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
echo SCRIPT: $SCRIPT
OUTXML=prod_update/normal/$SCRIPT.xml
PRETTYOUTXML=prod_update/pretty/${SCRIPT}_pretty.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
#
cat >tmp/noi.awk <<EOF
/<NumberOfItems>1<\/NumberOfItems>/{next}
/<NumberOfItems \/>/{next}
{print}
EOF
awk -f tmp/noi.awk $PRETTYINXML >$PRETTYOUTXML
bin/syncupdate.sh
python src/xmldiff.py $INXML $OUTXML -o $DELTAXML
bin/syncdelta.sh
end=`date +%s.%N`
runtime=$( echo "($end - $start)/1.000" | bc )
echo Elapsed: $runtime seconds
