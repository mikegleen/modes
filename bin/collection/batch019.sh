#!/bin/zsh
#
# batch019.sh
# -----------
#
# Upload files from hrm/scan/S4extra. Two files have been moved to S4Extra_defer:
#     JB314    The accession number is wrong
#     SH26     Needs re-scannning; the stitching was wrong.
#     JB412-3  redone as they were not properly rotated.
#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
# for example bin/collection/batch006.sh => batch006
# See ZSH documentation section 14.1.4 Modifiers.
export BATCH=${0:t:r}
export REVISION=
export VERBOS=2
export MODESFILE=/Users/mlg/pyprj/hrm/modes/prod_update/normal/2023-03-30_batch019.xml
#
bin/collection/batch_sub.sh
