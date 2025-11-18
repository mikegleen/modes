#!/bin/zsh
TESTHOME=test/xml2csv
BIN=$TESTHOME/bin
$BIN/xml2csv.sh test18 --include $TESTHOME/csv/test17.csv --heading -v 3
