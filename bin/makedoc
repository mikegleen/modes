#!/bin/bash
set -e
eval "$(conda shell.bash hook)"
conda activate py313
pushd doc
touch source/*
make html
