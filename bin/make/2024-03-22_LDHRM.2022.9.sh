#!/bin/zsh
set -e
INCSV=tmp/in.csv
INXML=2024-02-01d_G1_to_G2.xml
OUTXML=2024-03-22_add_2022.9.xml
MERGEDXML=2024-03-22_merged_2022.9.xml
cat >tmp/in.csv <<EOF
Serial,Title,Author,OrganisationName,PublicationDate,Accuracy,Description,Location
JB1068,Monarchs of Merry England,"Carse, Roland",Alf Cooke,1910,circa,"Reprint in four parts, two coloured illustrations to each part",B4
EOF
cat >tmp/update.yml <<EOF
cmd: column
xpath: ./Identification/Title
---
cmd: column
xpath: ./Production/Person[Role="author"]/PersonName
title: Author
---
cmd: column
xpath: ./Production/Organisation[Role="publisher"]/OrganisationName
---
cmd: column
xpath: ./Production/Date[@elementtype="publication date"]/DateBegin
parent_path: ./Production/Date[@elementtype="publication date"]
title: PublicationDate
---
cmd: column
xpath: ./Production/Date[@elementtype="publication date"]/Accuracy
parent_path: ./Production/Date[@elementtype="publication date"]
title: Accuracy
---
cmd: column
xpath: ./Identification/BriefDescription
title: Description
---
cmd: column
xpath: ./ObjectLocation[@elementtype="current location"]/Location
xpath2: ./ObjectLocation[@elementtype="normal location"]/Location
title: Location
---
cmd: constant
xpath: ./ObjectLocation[@elementtype="current location"]/Date/DateBegin
title: Location Date
value: 1992
---
cmd: constant
xpath: ./Acquisition/Person[Role="acquired from"]/PersonName
value: Denis Brinsmead
---
cmd: constant
xpath: ./Acquisition/Method
value: gift
---
cmd: constant
xpath: ./Acquisition/SummaryText
parent_path: ./Acquisition
value: Part of the Joan Brinsmead collection
EOF
python src/csv2xml.py -o prod_make/normal/$OUTXML \
                      -c tmp/update.yml \
                      -i $INCSV -t etc/templates/normal/2023-12-03_books_template.xml \
                      -v 1
bin/syncmake.sh
python src/merge_xml.py prod_update/normal/$INXML prod_make/normal/$OUTXML tmp/$MERGEDXML -v 1
python src/sort_xml.py tmp/$MERGEDXML prod_update/normal/$MERGEDXML -v 1
bin/syncprod.sh
