#!/bin/zsh
#
# batch020.sh
# -----------
#
# Get new files from Google Drive High Res Images of the WHRT Collection
# that have been added since the previous collection.
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
export BATCH=${0:t:r}
export REVISION=
export VERBOS=1
export MODESFILE=prod_update/normal/2023-04-08a_measurement.xml
#
bin/collection/batch_sub.sh
