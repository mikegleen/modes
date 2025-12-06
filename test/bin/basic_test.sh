#!/bin/zsh
run () {
    test/${1}/bin/test_${1}.sh
}
set -e
run xmlupd
run xml2csv
run exhibition
run filter_xml
run update_from_csv
