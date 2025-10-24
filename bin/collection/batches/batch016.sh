#!/bin/zsh
#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
#     :t Remove all leading pathname components, leaving the final component (tail).
#     :r Remove a filename extension leaving the root name.
export BATCH=${0:t:r}
export REVISION=
export MODESFILE=/Users/mlg/pyprj/hrm/modes/prod_update/normal/2023-02-26_condition.xml
#
bin/collection/batch_sub.sh
