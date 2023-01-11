#!/bin/zsh
#
# batch010.sh
# -----------
#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
export BATCH=${0:t:r}
export REVISION=
export MODESFILE=prod_update/pretty/2022-06-30_unframed4_pretty.xml
#
bin/collection/batch_sub.sh
