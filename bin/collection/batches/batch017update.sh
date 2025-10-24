#!/bin/zsh
#
# Update the data for files without loading images.
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
#     :t Remove all leading pathname components, leaving the final component (tail).
#     :r Remove a filename extension leaving the root name.
export BATCH=${0:t:r}
export REVISION=
export MODESFILE=prod_update/normal/2023-03-15_dimensions.xml
export ACCN_FILE=../results/collection/list_collection/wordpress.2023-03-14.csv
#
bin/collection/batch_upd_sub.sh
