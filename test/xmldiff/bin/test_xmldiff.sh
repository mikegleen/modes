#!/bin/zsh
set -e
export tpath=test/xmldiff
export tfile=changed.xml
#
rm -f $tpath/results/$tfile
python src/xmldiff.py $tpath/xml/oldmaster.xml $tpath/xml/newmaster.xml --outfile $tpath/results/$tfile -v 0 $*
#
source test/bin/validate.sh $? $tfile
