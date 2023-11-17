#!/bin/zsh
#
# 2923-11-13_repair.sh
# --------------------
#
# Import letters
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
export BATCH=${0:t:r}
export REVISION=
export VERBOS=1
export MODESFILE=prod_update/normal/2023-11-14_merged.xml
export IMGDIR=../collection/flatwebimgs
BR=$BATCH
DESTDIR=../collection/etc/$BR
#
python src/web/x053_list_pages.py $IMGDIR $DESTDIR/${BR}_list.csv
wc $DESTDIR/${BR}_list.csv
python src/xml2csv.py $MODESFILE $DESTDIR/${BR}_step1.csv -c src/cfg/website.yml --include $DESTDIR/${BR}_list.csv --include_skip 0 --heading -b -l results/reports/${BR}_website.log -v 2
python src/web/recode_collection.py $DESTDIR/${BR}_step1.csv $DESTDIR/${BR}.csv -g $DESTDIR/${BR}_list.csv -v $VERBOS
echo final: `wc $DESTDIR/${BR}_list.csv`
