#!/bin/zsh
#
# batch025.sh
# -----------
#
# Import 2023 & 2024 accessions
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
export BATCH=${0:t:r}
export REVISION=A
export VERBOS=1
export MODESFILE=prod_update/normal/2024-10-09_postcard.xml
#
bin/collection/batch_sub.sh
