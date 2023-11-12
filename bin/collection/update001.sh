#!/bin/zsh
#
# update001.sh
# ------------
#
# Add display order
#
set -euo pipefail
pushd ~/pyprj/hrm/modes
#
NAME=update001
MODESFILE=prod_update/normal/2023-11-10_display_order.xml
# INCLUDEFILE produced by src/web/list_collection.py
INCLUDEFILE=/Users/mlg/pyprj/hrm/collection/etc/$NAME/wordpress.2023-11-10.csv
DESTDIR=/Users/mlg/pyprj/hrm/collection/etc/$NAME
python src/xml2csv.py $MODESFILE $DESTDIR/step1.csv -c src/cfg/website.yml --include $INCLUDEFILE --include_skip 0 --heading -b -l results/reports/${NAME}_website.log -v 2
python src/web/recode_collection.py $DESTDIR/step1.csv $DESTDIR/$NAME/$NAME.csv
#
bin/collection/batch_sub.sh
