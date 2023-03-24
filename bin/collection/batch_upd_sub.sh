#!/bin/zsh
#
# batch_upd_sub.sh
# ----------------
#
# Subroutine for creating the CSV file to be imported by the website system
# when updating existing collection items.
#
# Assumed to be in directory ~/pyprj/hrm/modes
# The caller must set:
#   BATCH     the name of the directory to contain the new CSV file
#             under ~/pyprj/hrm/collection/etc
#   REVISION  a number indicating a re-try of a batch, can be zero length
#   MODESFILE The XML file from which to extract the image's metadata
#   ACCN_FILE CSV file containing the accession numbers of the records to be
#             updated. To update all of the images in the collection, this file
#             is created by web/list_collection.py
#
# The following set command is "poor man's strict mode"
#   -e - abort on non-zero exit status
#   -u - abort on unbound variable
#   -o pipefail - abort on piping failure
set -euo pipefail
if [ -z "$REVISION" ]; then # if REVISION is zero-length
	BR=${BATCH}
else
	BR=${BATCH}.${REVISION}
fi
DESTDIR=../collection/etc/$BATCH
mkdir -p $DESTDIR
#
# Pull the relevant fields from the Modes XML file for the objects in the batch.
#
python src/xml2csv.py $MODESFILE $DESTDIR/${BR}_step1.csv -c src/cfg/website.yml --include ${ACCN_FILE} --include_skip 0 --heading -b -l results/reports/${BR}_website.log -v 2
#
# Modify the CSV file to included new and adjusted columns.
#
python src/web/recode_collection.py $DESTDIR/${BR}_step1.csv $DESTDIR/${BR}.csv
