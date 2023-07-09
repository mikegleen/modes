#!/bin/zsh
xmllint --format test/update_from_csv/results/$1.xml > test/update_from_csv/results/${1:l}f.xml

