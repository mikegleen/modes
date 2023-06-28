#!/bin/zsh
tname=${1:u}
shift
python src/update_from_csv.py test/update_from_csv/xml/${tname}.xml test/update_from_csv/results/${tname}.xml -c test/update_from_csv/yml/${tname}.yml -m test/update_from_csv/csv/${tname:l}.csv $*
