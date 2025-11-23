#!/bin/zsh
tpath=test/filter_xml
result=filtered.xml
rm -f $tpath/results/$result
python src/filter_xml.py $tpath/xml/master.xml $tpath/results/$result -j TEST01 -v 0
#
source test/bin/validate.sh $? $result
