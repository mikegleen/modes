#!/bin/zsh
set -e
INXML=2024-04-07_JB119.xml
OUTXML=2024-04-14_del_filename.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
OUTCSV=tmp/$SCRIPT.csv
echo SCRIPT: $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
cmd: delete
xpath: ./References[Filename]
parent_path: .
EOF
python src/xml2csv.py prod_update/normal/$INXML results/reports/$SCRIPT.csv --heading
python src/update_from_csv.py prod_update/normal/$INXML \
                              prod_update/normal/$OUTXML \
                              -m results/reports/$SCRIPT.csv \
                              -c tmp/$SCRIPT.yml -a
