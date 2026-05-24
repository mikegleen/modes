#!/bin/zsh
#
# Reformat Classification elements
#
# Step 2. Delete all Classification elements and insert the ones that we've extracted and reformatted.
#
# Input: CSV file produced by step 1: tmp/2026-05-23_classification_expanded.csv
#           and manually reformatted: tmp/2026-05-23_classification_modified.csv
#
# Output: updated XML file
#
set -e
INXML=$(python src/utl/x066_latest.py -i prod_save/normal)
INCSV=results/reports/2026-05-23_classification_modified.csv
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
TEMPXML=tmp/normal/${SCRIPT}.xml
OUTXML=prod_update/normal/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
# echo  SCRIPT = $SCRIPT
# cat >/dev/null <<COMMENTOUT
cat >tmp/$SCRIPT.yml <<EOF
cmd: delete_all
xpath: ./Identification/Classification
parent_path: ./Identification
title: deletes
---
cmd: constant
title: Classification
xpath: ./Identification/Classification
parent_path: ./Identification
value:
---
cmd: multiple
title: Keywords
xpath: ./Identification/Classification/Keyword
parent_path: ./Identification/Classification
---
EOF
#
echo python src/update_from_csv.py $INXML --outfile $TEMPXML --mapfile $INCSV --cfgfile tmp/$SCRIPT.yml -v 1
python src/update_from_csv.py $INXML --outfile $TEMPXML --mapfile $INCSV --cfgfile tmp/$SCRIPT.yml -v 1
#
# Add blank Keyword entries where needed.
#
# Create a CSV file with the object numbers without Classification
#
python src/xml2csv.py $INXML tmp/objects2.csv  --heading --exclude --include $INCSV
cat >tmp/$SCRIPT.yml <<EOF
cmd: delete_all
xpath: ./Identification/Classification
parent_path: ./Identification
title: deletes
---
cmd: constant
title: Identification
xpath: ./Identification
parent_path: .
value:
---
cmd: constant
title: Classification
xpath: ./Identification/Classification
parent_path: ./Identification
value:
---
cmd: constant
xpath: ./Identification/Classification/Keyword
parent_path: ./Identification/Classification
value:
---
EOF
# COMMENTOUT
echo python src/update_from_csv.py $TEMPXML --outfile $OUTXML --cfgfile tmp/$SCRIPT.yml --deltafile $DELTAXML --mapfile tmp/objects2.csv
python src/update_from_csv.py $TEMPXML --outfile $OUTXML --cfgfile tmp/$SCRIPT.yml --deltafile $DELTAXML --mapfile tmp/objects2.csv -v 1
bin/synctmp.sh
bin/syncupdate.sh
