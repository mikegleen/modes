#!/bin/zsh
#   capture.sh -- copy new test results to baseline
#
pth=${1%/}  # remove trailing slash
oldpath=$pth/results
newpath=$pth/baseline
if [[ ! -a $oldpath ]]; then
    echo $oldpath does not exist.
    exit
fi
if [[ ! -a $newpath ]]; then
    echo $newpath does not exist.
    exit
fi
for file in $oldpath/*; do
    # echo $file
    fn=`basename $file`
    # echo $fn
    if [[ ! -a $newpath/$fn ]]; then
        echo cp $oldpath/$fn $newpath
        cp $oldpath/$fn $newpath
    fi
done

