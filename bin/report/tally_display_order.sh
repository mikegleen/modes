#!/bin/zsh
set -e
INXML=2024-10-25_merged_batch026_accessions.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
column: display order
xpath: ./Description/Aspect[Keyword="display order"]/Reading
EOF
python src/utl/python_version.py 3 12
python src/tally_elts.py prod_update/normal/$INXML -c tmp/$SCRIPT.yml -v 2
