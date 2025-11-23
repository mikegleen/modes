#!/bin/zsh
infile=2025-09-16_accessions.xlsx
tfile=basictest.xml
tpath=$(dirname $(dirname $ZSH_ARGZERO))
rm -f $tpath/results/$tfile
python src/csv2xml.py -i $tpath/csv/$infile -o $tpath/results/$tfile -c $tpath/yml/basictest.yml -v 0 $*
#
source test/bin/validate.sh $? $tfile
