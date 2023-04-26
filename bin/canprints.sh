cat >tmp/canprints.yml <<EOF
cmd: ifeq
xpath: ./ObjectLocation[@elementtype="current location"]/Location
value: CAN Prints
---
cmd: column
xpath: ./Identification/Title
EOF
python src/xml2csv.py /Users/mlg/pyprj/hrm/modes/prod_update/normal/2023-04-21_loc.xml  tmp/canprints.csv -c tmp/canprints.yml

