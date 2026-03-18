#!/bin/zsh
#
# Revert the location records for the objects that were erroneously moved to
# JBG for the Sublime exhibition.
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
INXML=prod_save/normal/2026-03-15s_prod_save_sorted.xml
#
#   bin/exhibition/2026-03-15_sublime.sh -> 2026-03-15_sublime
SCRIPT=${ZSH_ARGZERO:t:r}  # ZSH doc 14.1.4 Modifiers
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
cat >tmp/$SCRIPT.csv <<END
Serial
JB642
JB435
END
python src/location.py update --revert \
                              --infile $INXML \
                              --mapfile tmp/$SCRIPT.csv \
                              --outfile prod_update/normal/$OUTXML \
                              --deltafile prod_delta/normal/$DELTAXML
bin/syncupdate.sh
bin/syncdelta.sh
