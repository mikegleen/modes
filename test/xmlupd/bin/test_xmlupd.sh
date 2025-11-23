#!/bin/zsh
export tpath=test/xmlupd
export tfile=newmaster.xml
#
rm -f $tpath/results/$tfile
python src/xmlupd.py $tpath/xml/master.xml $tpath/xml/detail.xml -o $tpath/results/$tfile -v 0 $*
#
source test/bin/validate.sh $? $tfile
