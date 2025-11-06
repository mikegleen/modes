#!/bin/zsh
set -e
pushd /Users/mlg/pyprj/hrm/modes
#
INXML=$(python src/utl/x066_latest.py -i prod_save/normal)
OUTXML=${INXML: :-4}_sorted.xml
python src/sort_xml.py $INXML $OUTXML
bin/syncsave.sh
