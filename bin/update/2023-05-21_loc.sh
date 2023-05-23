#!/bin/zsh
INXML=2023-04-27_canprints2.xml
OUTXML=2023-05-21_loc.xml
cat >tmp/map.csv <<EOF
Serial,Location,LocationType,Patched,Reason
JB457,S22,cn,,box size
JB465,S22,cn,,box size
JB467,S22,cn,,box size
JB398,S22,cn,,box size
JB175,S8,cn,,box size
EOF
python src/location.py update -i prod_update/normal/$INXML -o prod_update/normal/$OUTXML --col_loc_type c --col_patch d --col_reason e -m tmp/map.csv -s 1 -v 2 -a
bin/syncprod.sh
