#!/bin/zsh
tpath=test/xml2csv
tst=$1
shift
python src/xml2csv.py $tpath/xml/$tst.xml $tpath/results/$tst.csv -c $tpath/yml/$tst.yml -v 0 $*
#
source test/bin/validate.sh $? $tst.csv
