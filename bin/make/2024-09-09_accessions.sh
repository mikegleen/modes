#!/bin/zsh
set -e
INCSV=data/acquisitions/2024-09-06/2024-09-12_MergedAccessions.csv
#
# Input XML file containing the full database in prod_update/normal/
INXML=2024-09-09_author.xml
#
# Output XML file containing the new Object records in prod_make/normal/
OUTXML=2024-09-13_accessions.xml
#
# Output XML file containing the merged and sorted new full database in prod_update/normal
MERGEDXML=2024-09-13_merged accessions.xml
cat >tmp/update.yml <<EOF
cmd: global
template_title: Template
template_dir: /Users/mlg/pyprj/hrm/modes/templates/normal
templates:
  Book: book_template.xml
  Ephemera: ephemera_template.xml
  Artwork: Original_Artwork_template.xml
  Reproduction: reproduction_template.xml
---
cmd: column
title: OE Number
xpath: ./Entry/EntryNumber
---
cmd: column
xpath: ./Identification/Title
---
cmd: column
title: Description
xpath: ./Identification/BriefDescription
---
cmd: column
title: Created by
xpath: ./Production/Person[Role="artist"]/PersonName
person_name:
if_other_column: Template
if_other_column_value: Artwork | Reproduction
---
cmd: column
title: Created by 2
xpath: ./Production/Person[Role="author"]/PersonName
column_title: Created by
if_other_column: Template
if_other_column_value: Book
---
cmd: column
title: Date produced
xpath: ./Production/Date/DateBegin
date:
if_other_column: Template
if_other_column_value: Artwork | Reproduction
---
cmd: column
xpath: ./Production/Date/Accuracy
parent_path: ./Production/Date
---
cmd: column
title: Date published
xpath: ./Production/Date[@elementtype="publication date"]
date:
if_other_column: Template
if_other_column_value: Book | Ephemera
---
cmd: column
title: Date published artwork
xpath: ./References/Reference[@elementtype="First Published In"]/Date
column_title: Date published
date:
if_other_column: Template
if_other_column_value: Artwork
---
cmd: column
title: First published in
xpath: ./References/Reference[@elementtype="First Published In"]/Title
if_other_column: Template
if_other_column_value: Artwork
---
cmd: column
title: Date published book
xpath: ./Production/Date[@elementtype="publication date"]
column_title: Date published
if_other_column: Template
if_other_column_value: Book | Ephemera
---
cmd: column
title: Date acquired
xpath: ./Acquisition/Date
date:
---
cmd: column
title: Acquired from
xpath: ./Acquisition/Person[Role="acquired from"]/PersonName
---
cmd: column
title: Acquired from organisation
xpath: ./Acquisition/Organisation[Role="acquired from"]/OrganisationName
---
cmd: column
title: Acquisition method
xpath: ./Acquisition/Method
---
cmd: column
title: Size mm Hxw
xpath: ./Description/Measurement[Part="image"]/Reading
if_other_column: Template
if_other_column_value: Artwork | Reproduction
---
cmd: column
title: Size mm Hxw books
column_title: Size mm Hxw
xpath: ./Description/Measurement/Reading
if_other_column: Template
if_other_column_value: Book | Ephemera
---
cmd: column
title: Medium
xpath: ./Description/Material[Part="medium"]/Keyword
---
cmd: column
title: Location
xpath: ./ObjectLocation[@elementtype="current location"]/Location
xpath2: ./ObjectLocation[@elementtype="normal location"]/Location
---
cmd: column
title: Pages
xpath: ./Description/Aspect[Keyword="pages"]/Reading
---
cmd: column
title: Condition
xpath: ./Description/Condition/Note
---
cmd: column
title: Notes
xpath: ./Notes
---
cmd: column
title: Publisher
xpath: ./Production/Organisation[Role="publisher"]/OrganisationName
---
cmd: column
title: ISBN
xpath: ./Production/ReferenceNumber[@elementtype="ISBN"]
---
cmd: column
title: Duplicate of
xpath: ./RelatedObject[@elementtype="duplicates"]
parent_path: .
attribute: elementtype
attribute_value: duplicates
---
cmd: column
title: Pages notes
xpath: ./Description/Aspect[Keyword="pages"]/Notes
parent_path: ./Description/Aspect[Keyword="pages"]
EOF
python src/csv2xml.py -o prod_make/normal/$OUTXML \
                      -c tmp/update.yml \
                      -i $INCSV -t etc/templates/normal/2023-12-03_books_template.xml \
                      -v 1 --skip 1
bin/syncmake.sh
python src/merge_xml.py prod_update/normal/$INXML prod_make/normal/$OUTXML tmp/$MERGEDXML -v 1
python src/sort_xml.py tmp/$MERGEDXML prod_update/normal/$MERGEDXML -v 1
bin/syncprod.sh
