#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
export BATCH=batch005
export REVISION=
export MODESFILE=prod_update/normal/2022-04-11_set_circa.xml
#
bin/collection/batch_sub.sh
