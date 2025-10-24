#!/bin/zsh
#
# batch025_shrink.sh
# -----------
#
# Import 2023 & 2024 accessions
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
BATCH=${0:t:r}
REVISION=
VERBOS=3
MODESFILE=prod_update/normal/2024-09-28_fix_sizes.xml
#
cat >tmp/incsv.csv <<EOF
Serial,HxW
LDHRM.2024.24.1-6,90x140
EOF
# python src/web/shrinkjpg.py ../collection/candidates_large/batch025_large ../collection/aawebimgs/batch025  --incsv tmp/incsv.csv -v 3 --nocolor
# python src/web/shrinkjpg.py ../collection/candidates_large/postcards ../collection/aawebimgs/batch025  --incsv tmp/incsv.csv -v 2 --nocolor
python src/web/shrinkjpg.py ../collection/candidates_large/batch025_large ../collection/aawebimgs/batch025 --inxml $MODESFILE --incsv tmp/incsv.csv -v $VERBOS -t tmp/trace.txt --dryrun
#
# Handle the Harry Tate picture specially
#
# python src/web/shrinkjpg.py ../collection/candidates_large/batch025_harry_tate ../collection/aawebimgs/batch025  -v $VERBOS -t tmp/trace.txt -m 2000
