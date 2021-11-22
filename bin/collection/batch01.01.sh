#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
pushd ~/pyprj/hrm/modes
BATCH=batch1
REVISION=.01
BR=${BATCH}${REVISION}
MODESFILE=prod_update/normal/2021-11-21a_type.xml
#MODESFILE=prod_update/pretty/2021-11-19b_type_pretty_test.xml
#
# Create a CSV file with the accession numbers from the filenames in the batch
#
python src/dir2csv.py ../collection/webimgs/${BATCH} tmp/${BR}_list.csv --heading
#
# Pull the relevant fields from the Modes XML file for the objects in the batch
#
python src/xml2csv.py $MODESFILE tmp/${BR}_step1.csv -c src/cfg/website.yml --include tmp/${BR}_list.csv --include_skip 1 --heading -v 2 -b -l results/reports/${BR}_website.txt
#
# Modify the CSV file to included new and adjusted columns.
#
python src/web/recode_collection.py tmp/${BR}_step1.csv ../collection/etc/${BATCH}/${BR}.csv
