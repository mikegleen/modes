#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
export BATCH=batch003
export REVISION=
export BR=${BATCH}${REVISION}
export MODESFILE=prod_update/normal/2012-11-29_first_pub.xml
#
bin/collection/batch_sub.sh
