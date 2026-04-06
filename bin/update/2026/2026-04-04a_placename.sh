#!/bin/zsh
#
#   Return the Sublime picture back to the store
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
INXML=prod_update/pretty/2026-03-17d_line_pretty.xml
INXML=prod_save/pretty/2026-04-04s_prod_save_sorted_pretty.xml
echo INXML = $INXML
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
OUTXML=prod_update/pretty/${SCRIPT}_pretty.xml
echo OUTXML= $OUTXML
DELTAXML=${SCRIPT}_delta_pretty.xml
sed 's/PlaceName>Joan Brinsmead Gallery/PlaceName>Heath Robinson Museum/' <$INXML >$OUTXML
python src/xmldiff.py $INXML $OUTXML --outfile prod_delta/pretty/$DELTAXML
bin/syncupdate.sh
bin/syncdelta.sh
