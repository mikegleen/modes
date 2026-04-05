#!/bin/zsh
set -e
INXML=$(python src/utl/x066_latest.py -i prod_save/normal)
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
OUTCSV=tmp/$SCRIPT.csv
# echo  SCRIPT = $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: if
xpath: ./Description/Measurement[Part="mount"]/Reading
---
column: Mount Reading
xpath: ./Description/Measurement[Part="mount"]/Reading
---
EOF
python src/xml2csv.py $INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
