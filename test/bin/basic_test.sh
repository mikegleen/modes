#!/bin/zsh
run () {
    # echo begin test: $1
    test/${1}/bin/test_${1}.sh
    # echo end test: $1
}
#
run xmlupd
run xml2csv
run exhibition
run filter_xml
run update_from_csv
