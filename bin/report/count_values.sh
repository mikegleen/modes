#!/bin/zsh
set -e
INXML=$(python src/utl/x066_latest.py -i prod_save/normal)
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
OUTCSV=tmp/$SCRIPT.csv
# echo  SCRIPT = $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
column: Role
xpath: ./Production/Person/Role
---
EOF
python src/utl/count_values.py $INXML --cfgfile tmp/$SCRIPT.yml
