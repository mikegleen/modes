#!/bin/zsh
set -e
export tpath=test/mergexml
export tfile=merged.xml
#
rm -f $tpath/results/$tfile
python src/mergexml.py $tpath/xml/oldmaster.xml $tpath/xml/newmaster.xml --outfile $tpath/results/$tfile -v 0 $*
#
source test/bin/validate.sh $? $tfile
