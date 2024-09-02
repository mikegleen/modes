#!/bin/zsh
set -e
INXML=2024-09-01a_part.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
OUTCSV=tmp/$SCRIPT.csv
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: ifattribeq
xpath: .
attribute: elementtype
value: cutting
---
cmd: attrib
xpath: .
attribute: elementtype
---
cmd: count
xpath: ./Description/Measurement
---
cmd: count
xpath: ./Description/Measurement/Part
---
cmd: column
xpath: ./Description/Measurement[1]/Part
title: part 1
---
cmd: column
xpath: ./Description/Measurement[2]/Part
title: part 2
---
cmd: column
xpath: ./Description/Measurement[3]/Part
title: part 3
---
EOF
python src/xml2csv.py prod_update/normal/$INXML results/reports/$SCRIPT.csv -b -c tmp/$SCRIPT.yml --heading
