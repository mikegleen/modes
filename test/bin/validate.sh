#!/bin/zsh
RED='\033[0;31m'
NC='\033[0m' # No Color
unsetopt errexit
#
#   Caller must pass $? from the program under test down as the first parameter.
#   Second parameter is the name of the result file to compare.
#
#
#   Get the path of the parent of the results and baseline dirctories:
#   test/exhibition/bin/test_exhibition.sh -> test/exhibition
tpath=$(dirname $(dirname $ZSH_ARGZERO))
if [[ $1 -ne 0 ]]; then
    printf "${RED}Test aborted. Python error exited.${NC} (${ZSH_ARGZERO:t:r})\n"
    exit
fi
if [[ ! -f $tpath/results/$2 ]]; then
    printf "${RED}Test aborted. No results file.${NC} (${ZSH_ARGZERO:t:r})\n"
    exit
fi
if [[ -f $tpath/baseline/$2 ]]; then
    diff -q $tpath/baseline/$2 $tpath/results/$2 >/dev/null
    diffreturn=$?
    if [[ $diffreturn -ne 0 ]]; then
        printf "${RED}Test failed.${NC} (${ZSH_ARGZERO:t:r})\n"
    else
        printf "Test passed. (${ZSH_ARGZERO:t:r})\n"
    fi
else
    cp $tpath/results/$2 $tpath/baseline
    echo Initializing baseline.
fi
