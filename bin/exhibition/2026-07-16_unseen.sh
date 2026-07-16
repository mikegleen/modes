#!/bin/bash
#
#   Update the Exhibition and Location records for the Unseen exhibition.
#
set -e
pushd /Users/mlg/pyprj/hrm/modes
INXML=prod_update/normal/2026-07-15_line2store.xml
echo INXML = $INXML
#
# "%.*" deletes from the right a period and everything after it
# So in this case, delete the ".sh".
SCRIPT="$(basename -- "${0%.*}")"
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
EXHIBITION=45
MAPFILE=tmp/$SCRIPT.csv
cat >$MAPFILE <<EOF
Serial
JB27
JB32
JB59
JB52
jb53
jb54
JB38
jb39
jb40
JB88
JB1009
JB1063
JB117
JB116
JB119
JB127
JB134
JB143
JB138
JB221
JB626
JB215
JB220
JB177
JB10
JB173
JB174
SH48
JB369
JB632
JB227
SH68.13
SH68.24
JB1203.46
LDHRM.2019.9
JB1019
JB1027
JB1018
JB1044
JB803
JB801
JB806
JB802
JB804
EOF
#
python src/exhibition.py    $INXML \
                            --mapfile $MAPFILE \
                            --outfile prod_update/normal/$OUTXML \
                            --deltafile prod_delta/normal/$DELTAXML \
                            --exhibition $EXHIBITION \
                            --move_to_location \
                            --location 'Joan Brinsmead Gallery' \
                            --verbose 1
#
bin/syncupdate.sh
bin/syncdelta.sh
