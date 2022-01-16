#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
# Batch 4 -- Children's Stories
#
pushd ~/pyprj/hrm/modes
export BATCH=batch004
export REVISION=
export BR=${BATCH}${REVISION}
export MODESFILE=prod_update/normal/2022-01-15_exhibition.xml
#
# bin/collection/batch_sub.sh
#
# Pull the relevant fields from the Modes XML file for the objects in the batch.
#
python src/xml2csv.py $MODESFILE tmp/${BR}_step1.csv -c src/cfg/website.yml --include tmp/${BR}_list.csv --include_skip 0 --heading -v 1 -b -l results/reports/${BR}_website.log
#
# Modify the CSV file to included new and adjusted columns.
#
mkdir -p ../collection/etc/$BATCH
python src/web/recode_collection.py tmp/${BR}_step1.csv ../collection/etc/${BATCH}/${BR}.csv
