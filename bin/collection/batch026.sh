#!/bin/zsh
#
# batch026.sh
# -----------
#
# Import JB1217 letters
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
export BATCH=${0:t:r}
export REVISION=
export VERBOS=1
export MODESFILE=prod_update/normal/2024-10-21_edit.xml
#
bin/collection/batch_sub.sh
