#!/bin/zsh
#
awk -F , '$2 != $3 {print}' tmp/locs.csv
