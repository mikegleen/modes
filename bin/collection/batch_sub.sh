#!/bin/zsh
#
# Create a CSV file with the accession numbers from the filenames in the batch.
# Insert a heading in the CSV file even though it will be skipped by xml2csv (useful for debugging).
#
set -e
if [ -z "$REVISION" ]; then
	BR=${BATCH}
else
	BR=${BATCH}.${REVISION}
fi
DESTDIR=../collection/etc/$BATCH
mkdir -p $DESTDIR
python src/dir2csv.py ../collection/aawebimgs/${BATCH} tmp/${BR}_list.csv --heading
#
# Pull the relevant fields from the Modes XML file for the objects in the batch.
#
python src/xml2csv.py $MODESFILE $DESTDIR/${BR}_step1.csv -c src/cfg/website.yml --include tmp/${BR}_list.csv --include_skip 1 --heading -v 1 -b -l results/reports/${BR}_website.log
#
# Modify the CSV file to included new and adjusted columns.
#
python src/web/recode_collection.py $DESTDIR/${BR}_step1.csv $DESTDIR/${BR}.csv
