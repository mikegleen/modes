#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
export BATCH=batch003
export REVISION=
export BR=${BATCH}${REVISION}
export MODESFILE=prod_update/normal/2022-03-27_edit.xml
#
bin/collection/batch_sub.sh
