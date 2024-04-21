#!/bin/zsh
set -e
INXML=2024-04-07_JB119.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
cat >tmp/$SCRIPT.yml <<EOF
cmd: ifanyeq
xpath: ./Exhibition/Place
value: Dulwich Picture Gallery
EOF
python src/xml2csv.py prod_update/normal/$INXML results/reports/$SCRIPT.csv -c tmp/$SCRIPT.yml
