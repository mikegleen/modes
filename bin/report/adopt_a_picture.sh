#!/bin/zsh
cat >tmp/dirs.csv <<EOF
prod_save/normal
prod_update/normal
EOF
INXML=$(python src/utl/x066_latest.py -f tmp/dirs.csv)
# echo INXML = $INXML
DATE=$(date -I)
cat >tmp/adopt.yml <<EOF
cmd: ifeq
xpath: ./Association/Type
value: Adopt a Picture
---
cmd: column
xpath: ./Identification/Title
---
column: Donor
xpath: ./Association/Person/PersonName
---
column: Date Adopted
xpath: ./Association[Type="Adopt a Picture"]/Date
---
column: Dedication
xpath: ./Association/SummaryText/Note
---
column: Current Location
xpath: ./ObjectLocation[@elementtype="current location"]/Location
---
column: Conservator
xpath: ./Conservation/Name/PersonName
EOF
python src/xml2csv.py $INXML results/reports/${DATE}_adopt.csv -b -c tmp/adopt.yml --heading
