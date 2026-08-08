#!/bin/zsh
set -e
INXML=$(python src/utl/x066_latest.py -i prod_save/normal)
SCRIPT="$(basename -- "${0%.*}")"
OUTCSV=tmp/$SCRIPT.csv
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: if
xpath: ./Description/Aspect/Notes
title: ifAspect
---
cmd: column
xpath: ./Description/Aspect
title: Aspect
---
cmd: column
xpath: ./Description/Aspect/Reading
---
cmd: column
xpath: ./Description/Aspect/Notes
EOF
python src/xml2csv.py $INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
