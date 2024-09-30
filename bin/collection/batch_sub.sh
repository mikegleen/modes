#!/bin/zsh
#
# batch_sub.sh
# ------------
#
# Subroutine for creating the CSV file to be imported by the website system
# Assumed to be in directory ~/pyprj/hrm/modes
# The caller must set:
#   BATCH     the name of the directory containing the new JPG files
#             under ~/pyprj/hrm/collection/aawebimgs/
#   REVISION  a number indicating a re-try of a batch, can be zero length
#   MODESFILE The XML file from which to extract the image's metadata
#   VERBOS    The verbosity level
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
IMGDIR=../collection/aawebimgs/${BATCH}
DESTDIR=../collection/etc/$BATCH
mkdir -p $DESTDIR
#
# Insert a heading in the CSV file even though it will be skipped by xml2csv (useful for debugging).
# Although it is called a CSV file, there is only one column, the accession number.
#
# Create a file with the accession numbers in column 1 and a "|" delimited list of filenames
# in column 2. There is no heading row.
#
python src/web/x053_list_pages.py ../collection/aawebimgs/$BR ../collection/etc/${BR}/${BR}_list.csv
#
# Pull the relevant fields from the Modes XML file for the objects in the batch.
#
python src/xml2csv.py $MODESFILE $DESTDIR/${BR}_step1.csv -c src/cfg/website.yml --include ../collection/etc/batch023/${BR}_list.csv --include_skip 1 --heading -b -l results/reports/${BR}_website.log -v 2
#
# Modify the CSV file to included new and adjusted columns.
#
python src/web/recode_collection.py $DESTDIR/${BR}_step1.csv $DESTDIR/${BR}.csv --imgcsvfile ../collection/etc/batch023/${BR}_list.csv -v $VERBOS
