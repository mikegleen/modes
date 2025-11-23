#!/bin/zsh
set -e
tfile=test1.xml
tpath=$(dirname $(dirname $ZSH_ARGZERO))
rm -f $tpath/results/$tfile
python src/update_from_csv.py $tpath/xml/test1.xml -o $tpath/results/test1.xml -c $tpath/yml/test1.yml -m $tpath/csv/test1.csv -v 0 $*
#
source test/bin/validate.sh $? $tfile
