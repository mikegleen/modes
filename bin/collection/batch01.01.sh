#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
export BATCH=batch1
export REVISION=.01
export BR=${BATCH}${REVISION}
export MODESFILE=prod_update/normal/2021-11-21a_type.xml
#MODESFILE=prod_update/pretty/2021-11-19b_type_pretty_test.xml
#
bin/collection/batch_sub.sh
