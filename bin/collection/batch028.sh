#!/bin/zsh
#
# batch028.sh
# -----------
#
# Import images from the Permanent Exhibition folder on Google Drive
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
export BATCH=${0:t:r}
export REVISION=
export ADDENDUM=batch028_addendum.csv
export VERBOS=1
export MODESFILE=prod_update/normal/2025-04-03a_county.xml
#
bin/collection/batch_sub.sh
