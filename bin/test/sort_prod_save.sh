#!/bin/zsh
set -e
pushd /Users/mlg/pyprj/hrm/modes
#
INXML=$(python src/utl/x066_latest.py -i prod_save/normal)
INXMLM=$(python src/utl/x066_latest.py -i prod_save/normal --modify)
OUTXML=${INXMLM: :-4}_sorted.xml
# python src/sort_xml.py -i $INXML -o $OUTXML
# rm $INXML
# bin/syncsave.sh
echo $INXML
echo $INXMLM
echo $(basename ${INXML%.*})
