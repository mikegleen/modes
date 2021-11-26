#
# Create a CSV file with the accession numbers from the filenames in the batch.
# Insert a heading in the CSV file even though it will be skipped by xml2csv for debugging.
#
set -e
python src/dir2csv.py ../collection/webimgs/${BATCH} tmp/${BR}_list.csv --heading
#
# Pull the relevant fields from the Modes XML file for the objects in the batch.
#
python src/xml2csv.py $MODESFILE tmp/${BR}_step1.csv -c src/cfg/website.yml --include tmp/${BR}_list.csv --include_skip 1 --heading -v 3 -b -l results/reports/${BR}_website.txt
#
# Modify the CSV file to included new and adjusted columns.
#
mkdir -p ../collection/etc/$BATCH
python src/web/recode_collection.py tmp/${BR}_step1.csv ../collection/etc/${BATCH}/${BR}.csv
