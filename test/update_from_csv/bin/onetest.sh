#!/bin/zsh
set -e
tname=${1:u}
shift
tu=test/update_from_csv
python src/update_from_csv.py $tu/xml/${tname}.xml $tu/results/${tname}.xml -c $tu/yml/${tname}.yml -m $tu/csv/${tname:l}.csv $*
$tu/bin/lint.sh $tname
