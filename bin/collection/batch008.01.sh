#!/bin/zsh
#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
export BATCH=${0:t:r}
export REVISION=01
export MODESFILE=prod_update/normal/2022-04-27_jb366.xml
#
bin/collection/batch_sub.sh
