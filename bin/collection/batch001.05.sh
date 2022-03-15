#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
export BATCH=batch001
export REVISION=.05
export BR=${BATCH}${REVISION}
export MODESFILE=prod_update/pretty/2022-03-13_dulwich2_pretty.xml
#
bin/collection/batch_sub.sh
