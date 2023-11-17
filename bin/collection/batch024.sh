#!/bin/zsh
#
# batch024.sh
# -----------
#
# Import letters
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
export BATCH=${0:t:r}
export REVISION=
export VERBOS=1
export MODESFILE=??????????
export IMGDIR=../collection/aawebimgs/batch023
#
bin/collection/batch_sub.sh
