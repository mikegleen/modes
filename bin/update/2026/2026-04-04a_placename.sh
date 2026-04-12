#!/bin/bash
#
#   Return the Sublime picture back to the store
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
INXML=prod_save/pretty/2026-04-04s_prod_save_sorted_pretty.xml
echo INXML = $INXML
SCRIPT="$(basename -- "${0%.*}")"
OUTXML=prod_update/pretty/${SCRIPT}_pretty.xml
echo OUTXML=$OUTXML
DELTAXML=${SCRIPT}_delta_pretty.xml
sed 's/PlaceName>Joan Brinsmead Gallery/PlaceName>Heath Robinson Museum/' <$INXML >$OUTXML
python src/xmldiff.py $INXML $OUTXML --outfile prod_delta/pretty/$DELTAXML
bin/syncupdate.sh
bin/syncdelta.sh
