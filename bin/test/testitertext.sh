#!/bin/zsh
#
#   Test the elementtree.itertext function
#
set -e
# python src/utl/count_values.py  data/test/one_object.xml \
#                                 --xpath ./Production \
#                                 --itertext
python src/utl/count_values.py  /Users/mlg/pyprj/hrm/modes/prod_update/normal/2025-02-07_stocktake_loc.xml \
                                --xpath ./Content \
                                --itertext --report
# python src/utl/count_values.py  /Users/mlg/pyprj/hrm/modes/data/test/test_itertext.xml \
#                                 --xpath ./Content \
#                                 --itertext --report
