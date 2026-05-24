#!/usr/bin/env bash
echo begin find errors
pushd doc
if [[ -n ${1+x} ]]; then  # true if parameter exists
    echo testing source/$1.rst
    touch source/$1.rst
    make html
    exit
fi
#
for file in source/*.rst ; do
    touch $file
    echo file: $file
    make html
done
