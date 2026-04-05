#!/bin/bash
# set -e
eval "$(conda shell.bash hook)"
conda activate py313
pushd doc
for f in source/*; do
    echo testing $f
    touch $f
    make html
done
