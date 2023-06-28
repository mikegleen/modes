#!/bin/zsh
ap=test/update_from_csv/bin/update_from_csv.sh
tl=test/update_from_csv/bin/testlist.txt
testsrun=0
#testsfailed=0
#
function runn {
    let "testsrun++"
    if [[ "${tst:0:1}" == "-" ]] ; then
        tst=${tst:1}
    fi
    $ap "$@"
    if (( $? ))
    then
        let testsfailed++
    fi
}
# The '=' sign forces the string to expand to an array
while read -r; do
    runn ${=REPLY}
done < $tl
#
RED='\033[0;31m'
GREEN='\033[0;32m'
NOCOLOR='\033[0m'
echo $testsrun tests run.
if [[ ! $testsfailed ]]; then
    echo ${GREEN}All tests passed.${NOCOLOR}
else
    echo ${RED}$testsfailed tests failed.${NOCOLOR}
fi
