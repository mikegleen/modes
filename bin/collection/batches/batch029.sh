#!/bin/zsh
#
# batch029.sh
# -----------
#
# Import images from the Permanent Exhibition folder on Google Drive
#
set -e
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
export BATCH=${0:t:r}
export REVISION=
export ADDENDUM=
export VERBOS=1
export MODESFILE=$(python src/utl/x066_latest.py -i prod_update/normal)
echo MODESFILE: $MODESFILE
#
bin/collection/batch_sub.sh
