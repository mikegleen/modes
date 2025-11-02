#!/bin/zsh
#
# batch_sub.sh
# ------------
#
# Subroutine for creating the CSV file to be imported by the website system
# The current directory is assumed to be ~/pyprj/hrm/modes
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
	BR=${BATCH}${REVISION}
fi
IMGDIR=../collection/aawebimgs/${BR}
DESTDIR=../collection/etc/$BATCH
mkdir -p $DESTDIR
#
# Create a file with the accession numbers in column 1 and a "|" delimited list of image
# filename in column 2. There is no heading row.
#
python src/web/x053_list_pages.py $IMGDIR ${DESTDIR}/${BR}_list.csv
#
# Pull the relevant fields from the Modes XML file for the objects in the batch.
#
python src/xml2csv.py $MODESFILE $DESTDIR/${BR}_modesdata.csv \
                      --cfgfile src/cfg/website.yml \
                      --include ${DESTDIR}/${BR}_list.csv \
                      --logfile results/reports/${BR}_website.log \
                      --heading --bom --verbose $VERBOS
#
# Modify the CSV file to included new and adjusted columns.
#
if [ -z "$ADDENDUM" ] ; then
python src/web/recode_collection.py --incsvfile $DESTDIR/${BR}_modesdata.csv --outfile $DESTDIR/${BR}.csv --imgcsvfile $DESTDIR/${BR}_list.csv -v $VERBOS
else
python src/web/recode_collection.py --incsvfile $DESTDIR/${BR}_modesdata.csv \
                                    --addendum $DESTDIR/$ADDENDUM \
                                    --outfile $DESTDIR/${BR}.csv \
                                    --imgcsvfile $DESTDIR/${BR}_list.csv \
                                    -v $VERBOS
fi
