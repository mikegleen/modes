#
# For the files in a batch, create the CSV file to be uploaded to WordPress for the collection images.
#
set -e
BATCH=batch2
MODESFILE=prod_update/pretty/2021-11-21a_type.xml
#
# Create a CSV file with the accession numbers from the filenames in the batch
#
python src/dir2csv.py ../collection/candidates/${BATCH} tmp/${BATCH}_list.csv
#
# Pull the relevant fields from the Modes XML file for the objects in the batch
#
python src/xml2csv.py $MODESFILE tmp/${BATCH}_step1.csv -c src/cfg/website.yml --include tmp/${BATCH}_list.csv --include_skip 1 --heading -v 2 -b -l results/reports/${BATCH}_website.txt
#
# Modify the CSV file to included new and adjusted columns.
#
python src/web/recode_collection.py tmp/${BATCH}_step1.csv results/csv/collection/${BATCH}.csv
