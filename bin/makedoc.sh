#!/bin/bash
set -e
eval "$(conda shell.bash hook)"
conda activate py314
pushd doc
touch source/*
make html
