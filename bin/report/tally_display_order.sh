#!/bin/zsh
set -e
INXML=$(python src/utl/x066_latest.py -i prod_save/normal)
SCRIPT="$(basename -- "${0%.*}")"
# echo $SCRIPT
cat >tmp/$SCRIPT.yml <<EOF
column: display order
xpath: ./Description/Aspect[Keyword="display order"]/Reading
EOF
python src/utl/python_version.py 3.14
python src/tally_elts.py $INXML -c tmp/$SCRIPT.yml -v 1
