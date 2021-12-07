#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
export BATCH=batch001
export REVISION=.02
export BR=${BATCH}${REVISION}
export MODESFILE=prod_save/normal/2021-12-01_prod_save.xml
#
bin/collection/batch_sub.sh
