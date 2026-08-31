#!/bin/zsh
set -e
INXML=$(python src/utl/x066_latest.py -i prod_save/normal)
SCRIPT="$(basename -- "${0%.*}")"
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: column
xpath: ./Identification/Title
---
cmd: column
xpath: ./Identification/BriefDescription
EOF
python src/compare_elts.py $INXML -c tmp/$SCRIPT.yml` $*
