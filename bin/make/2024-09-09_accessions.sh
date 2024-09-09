#!/bin/zsh
set -e
INCSV=data/acquisitions/2024-09-06/2024-09-09_MergedAccessions.csv
#
# Input XML file containing the full database in prod_update/normal/
INXML=2024-09-07a_patch.xml
#
# Output XML file containing the new Object records in prod_make/normal/
OUTXML=2024-03-22_add_2022.9.xml
#
# Output XML file containing the merged and sorted new full database in prod_update/normal
MERGEDXML=2024-03-22_merged_2022.9.xml
cat >tmp/update.yml <<EOF
cmd: global
template_title: Type
template_dir: /Users/mlg/pyprj/hrm/modes/etc/templates/current_templates/normal
templates:
  Book: book_template.xml
  Ephemera: ephemera_template.xml
  Artwork: Original_Artwork_template.xml
---
cmd: column
xpath: ./Entry/EntryNumber
title: OE Number
---
cmd: column
xpath: ./Identification/Title
---
cmd: column
xpath: ./Identification/BriefDescription
title: Description
---
cmd: column
xpath:
title:
---
cmd: column
xpath:
title:
---
cmd: column
xpath:
title:
---
cmd: column
xpath:
title:
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
                      -v 1 --skip 1
bin/syncmake.sh
python src/merge_xml.py prod_update/normal/$INXML prod_make/normal/$OUTXML tmp/$MERGEDXML -v 1
python src/sort_xml.py tmp/$MERGEDXML prod_update/normal/$MERGEDXML -v 1
bin/syncprod.sh
