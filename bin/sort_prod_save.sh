#!/bin/zsh
set -e
pushd /Users/mlg/pyprj/hrm/modes
#
INXML=$(python src/utl/x066_latest.py -i prod_save/normal --skip_date_suffix s)
echo INXML=$INXML
INXMLM=$(python src/utl/x066_latest.py -i prod_save/normal --modify s --skip_date_suffix s)
echo INXMLM=$INXMLM
OUTXML=${INXMLM: :-4}_sorted.xml
python src/sort_xml.py -i $INXML -o $OUTXML
rm $INXML
bin/syncsave.sh
