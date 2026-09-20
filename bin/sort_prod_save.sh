#!/bin/zsh
set -e
pushd /Users/mlg/pyprj/hrm/modes
#
# Only look at files that end with "prod_save.xml" and also don't have a date suffix of "s".
INXML=$(python src/utl/x066_latest.py -i prod_save/normal --skip_date_suffix s --re ".*prod_save\\.xml")
echo INXML=$INXML
INXMLM=$(python src/utl/x066_latest.py -i prod_save/normal --modify s --skip_date_suffix s --re ".*prod_save\\.xml")
echo INXMLM=$INXMLM
#
# Strip off the trailing "save.xml" and append "sorted.xml"
OUTXML=${INXMLM: :-9}_sorted.xml
echo OUTXML=$OUTXML
python src/sort_xml.py -i $INXML -o $OUTXML
rm $INXML
bin/syncsave.sh
