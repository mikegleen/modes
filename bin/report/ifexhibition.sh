#!/bin/zsh
set -e
INXML=`python src/utl/x066_latest.py -i prod_update/normal`
echo INXML= $INXML
SCRIPT=$ZSH_ARGZERO:t:r
OUTCSV=tmp/$SCRIPT.csv
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: ifexhib
value: ##VALUE##
---
cmd: column
xpath: ./Identification/Title
width: 50
---
EOF
sed -i.bak s/##VALUE##/$1/ tmp/$SCRIPT.yml
python src/xml2csv.py $INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
