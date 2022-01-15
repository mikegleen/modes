#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
export BATCH=batch001
export REVISION=.03
export BR=${BATCH}${REVISION}
export MODESFILE=prod_update/normal/2022-01-06_accuracy.xml
#
bin/collection/batch_sub.sh
