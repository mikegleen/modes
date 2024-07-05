#!/bin/zsh
set -e
INXML=2024-07-05_itemlist.xml
OUTXML=2024-07-05_postcards.xml
DELTAXML=2024-07-05_delta.xml
#
#   Step 1 - Create the Object element group for the postcards
#
cat >tmp/in.csv <<EOF
Serial
LDHRM:2024.24
EOF
cat >tmp/update.yml <<EOF
cmd: constant
xpath: ./Identification/Title
value: Ideal Home Postcards
---
cmd: constant
xpath: ./Identification/BriefDescription
value: Six postcards from the Daily Mail Ideal Home Exhibition in 1934
---
cmd: constant
xpath: ./ObjectLocation[@elementtype="current location"]/Location
xpath2: ./ObjectLocation[@elementtype="normal location"]/Location
value: G12
---
cmd: constant
xpath: ./ObjectLocation[@elementtype="current location"]/Date/DateBegin
title: Location Date
value: "{{today}}"
---
cmd: constant
xpath: ./Production/Date[@elementtype="publication date"]/DateBegin
parent_path: ./Production/Date[@elementtype="publication date"]
title: PublicationDate
value: 1934
---
cmd: constant
xpath: ./Production/Date[@elementtype="publication date"]/Accuracy
parent_path: ./Production/Date[@elementtype="publication date"]
value:
---
cmd: constant
xpath: ./Description/Measurement/Reading
value: 90mm x 140mm
---
cmd: constant
xpath: ./Acquisition/Person[Role="acquired from"]/PersonName
value: Gleen, Mike
---
cmd: constant
xpath: ./Acquisition/Method
value: purchase
---
cmd: constant
xpath: ./Acquisition/SummaryText
parent_path: ./Acquisition
value: Bought from eBay
---
cmd: constant
xpath: ./Entry/EntryNumber
value: 141
EOF
python src/csv2xml.py -o tmp/normal/step1.xml \
                      -c tmp/update.yml \
                      -i tmp/in.csv -t etc/templates/current_templates/normal/2024-07-04_ephemera_template.xml \
                      -v 1
#
# Step2 - Add the six postcards as Item elements
#
cat >tmp/in2.csv <<EOF
Serial,Title
2024.24.1,The Gadgets
2024.24.2,The Kitchen
2024.24.3,The Dining Room
2024.24.4,The Nursery
2024.24.5,The Bedroom
2024.24.6,The Garden
EOF
cat >tmp/update2.yml <<EOF
cmd: global
add_mda_code:
subid_grandparent: .
subid_parent: ItemList
---
cmd: column
xpath: Title
EOF
python src/update_from_csv.py tmp/normal/step1.xml tmp/normal/step2.xml -c tmp/update2.yml -m tmp/in2.csv -v 1
#
# Step 3. Create the placeholder Object for 2022.9
#
cat >tmp/in3.csv <<EOF
Serial
LDHRM:2022.9
EOF
cat >tmp/update3.yml <<EOF
EOF
python src/csv2xml.py -o tmp/normal/step3.xml \
                      -c tmp/update3.yml \
                      -i tmp/in3.csv -t etc/templates/current_templates/normal/2024-07-04_placeholder.xml \
                      -v 1
#
#
#
python src/xmldiff.py prod_update/normal/2024-06-01_measure.xml prod_update/normal/2024-07-05_itemlist.xml -o tmp/diff.xml
# step2 2024.24 (postcards)
# step3 2022.9  (placeholder)

python src/merge_xml.py -i tmp/normal/step2.xml -i tmp/normal/step3.xml -i tmp/diff.xml -o  prod_delta/normal/$DELTAXML -v 1
python src/merge_xml.py -i prod_update/normal/$INXML -i tmp/normal/step2.xml -i tmp/normal/step3.xml -o  tmp/merged.xml -v 1
bin/synctmp.sh
python src/sort_xml.py tmp/merged.xml prod_update/normal/$OUTXML -v 1
bin/syncprod.sh
bin/syncdelta.sh
