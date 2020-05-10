ap=test/update_from_csv/bin/update_from_csv.sh
testsrun=0
testsfailed=0
#
function run {
    let testsrun++
    $ap $*
    if (( $? != 0))
    then
        let testsfailed++
    fi
}
run TEST01 --heading -v 0
#
echo $testsrun tests run.
echo $testsfailed tests failed.
