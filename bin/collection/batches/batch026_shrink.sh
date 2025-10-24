#!/bin/zsh
#
# batch026_shrink.sh
# -----------
#
# Import JB1213.18-26 accessions
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
BATCH=${0:t:r}
REVISION=
VERBOS=3
MODESFILE=prod_update/normal/2024-10-25_merged_batch026_accessions.xml
#
# python src/web/shrinkjpg.py ../collection/candidates_large/batch025_large ../collection/aawebimgs/batch025  --incsv tmp/incsv.csv -v 3 --nocolor
# python src/web/shrinkjpg.py ../collection/candidates_large/postcards ../collection/aawebimgs/batch025  --incsv tmp/incsv.csv -v 2 --nocolor
python src/web/shrinkjpg.py ../collection/candidates_large/batch026_large ../collection/aawebimgs/batch026 --inxml $MODESFILE -v $VERBOS -t tmp/trace.txt --dryrun
#
