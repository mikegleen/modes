#!/bin/zsh
#
# batch021.sh
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
export MODESFILE=prod_update/normal/2023-10-14_batch021_type.xml
export IMGDIR=../collection/aawebimgs/batch021
#
bin/collection/batch_sub.sh
