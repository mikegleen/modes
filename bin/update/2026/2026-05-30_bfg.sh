#!/usr/bin/env bash
#
INXML=$(python src/utl/x066_latest.py -i prod_save/normal)
SCRIPT="$(basename -- "${0%.*}")"
OUTXML=prod_update/normal/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
echo INXML = $INXML
echo OUTXML=$OUTXML
cat >tmp/list.csv <<EOF
Serial
LDHRM.2019.14
LDHRM.2019.15
LDHRM.2019.18
LDHRM.2019.20
LDHRM.2019.21
LDHRM.2019.22
LDHRM.2019.24
LDHRM.2019.26
LDHRM.2019.27
LDHRM.2019.28
LDHRM.2019.29
LDHRM.2019.30
LDHRM.2019.31
LDHRM.2019.32
LDHRM.2019.34
LDHRM.2019.35
LDHRM.2019.36
EOF
python src/location.py update -i $INXML -o $OUTXML --mapfile tmp/list.csv --normal --location BFG --deltafile $DELTAXML -v 2
bin/syncupdate.sh
bin/syncdelta.sh
