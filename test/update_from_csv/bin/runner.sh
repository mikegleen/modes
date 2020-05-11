ap=test/update_from_csv/bin/update_from_csv.sh
tl=test/update_from_csv/bin/testlist.txt
testsrun=0
testsfailed=0
#
function run {
    let testsrun++
    $ap $*
    if (( $? != 0 ))
    then
        let testsfailed++
    fi
}
#
while read -r; do
    run $REPLY
done < $tl
#
echo $testsrun tests run.
echo $testsfailed tests failed.
