#!/bin/zsh
#
tfile=result1.xml
tpath=test/exhibition
#
touch $tpath/results/test
rm -f $tpath/results/*
python src/exhibition.py $tpath/xml/result1.xml -o $tpath/results/result1.xml -e 44 -m $tpath/csv/test1.csv -v 0
#
source test/bin/validate.sh $? $tfile
