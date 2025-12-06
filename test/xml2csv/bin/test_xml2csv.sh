#!/bin/zsh
set -e
tfile=test18.csv
tpath=$(dirname $(dirname $ZSH_ARGZERO))
rm -f $tpath/results/*
#
# Set lineterminator because git hates \r\n.
python src/xml2csv.py $tpath/xml/test18.xml $tpath/results/test18.csv --include $tpath/csv/test18.csv --heading --lineterminator "\\n" -v 0
#
source test/bin/validate.sh $? $tfile
