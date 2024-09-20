#!/bin/zsh
set -e
INCSV=data/acquisitions/2024-09-06/2024-09-18_MergedAccessions.xlsx
#
# Input XML file containing the full database in prod_update/normal/
INXML=2024-09-20_author_fix_Image.xml
#
# Output XML file containing the new Object records in prod_make/normal/
OUTXML=2024-09-20_accessions.xml
#
# Output XML file containing the merged and sorted new full database in prod_update/normal
MERGEDXML=2024-09-20_merged_accessions.xml
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
column: Title
xpath: ./Identification/Title
---
column: Description
xpath: ./Identification/BriefDescription
---
column: Created by
xpath: ./Production/Person[Role="artist"]/PersonName
person_name:
if_other_column: Template
if_other_column_value: Artwork | Reproduction
---
column: Created by 2
xpath: ./Production/Person[Role="author"]/PersonName
person_name:
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
if_other_column: Template
if_other_column_value: Artwork | Reproduction
---
cmd: column
title: Date published
xpath: ./Production/Date[@elementtype="publication date"]/DateBegin
parent_path: ./Production/Date[@elementtype="publication date"]
date:
if_other_column: Template
if_other_column_value: Book | Ephemera
---
cmd: column
title: Date published accuracy
xpath: ./Production/Date[@elementtype="publication date"]/Accuracy
parent_path: ./Production/Date[@elementtype="publication date"]
column_title: Accuracy
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
column: First published in
xpath: ./References/Reference[@elementtype="First Published In"]/Title
---
column: Date acquired
xpath: ./Acquisition/Date
date:
---
cmd: column
title: Acquired from
xpath: ./Acquisition/Person[Role="acquired from"]/PersonName
person_name:
---
cmd: column
title: Acquired from organisation
xpath: ./Acquisition/Organisation[Role="acquired from"]/OrganisationName
parent_path: ./Acquisition/Organisation[Role="acquired from"]/
---
cmd: column
title: Acquisition method
xpath: ./Acquisition/Method
---
cmd: column
title: Size mm HxW
xpath: ./Description/Measurement[Part="image"]/Reading
if_other_column: Template
if_other_column_value: Artwork | Reproduction
---
cmd: column
title: Size mm HxW books
column_title: Size mm HxW
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
title: Location datebegin
xpath: ./ObjectLocation[@elementtype="current location"]/Date/DateBegin
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
column: ISBN
xpath: ./Production/ReferenceNumber[@elementtype="ISBN"]
---
# cmd: column
# title: Duplicate of
# xpath: ./RelatedObject[@elementtype="duplicates"]
# parent_path: .
# attribute: elementtype
# attribute_value: duplicates
# ---
cmd: column
title: Pages notes
xpath: ./Description/Aspect[Keyword="pages"]/Notes
parent_path: ./Description/Aspect[Keyword="pages"]
---
cmd: reproduction
xpath: ./Reproduction/Filename
EOF
python src/csv2xml.py -o prod_make/normal/$OUTXML \
                      -c tmp/update.yml \
                      -i $INCSV \
                      -v 1 --serial "Accession Number"
bin/syncmake.sh
#
# Remove LDHRM.2024.24 as it had previously been inserted differently.
#
cat >tmp/filter.csv <<EOF
LDHRM.2024.24
EOF
python src/filter_xml.py prod_update/normal/$INXML tmp/filtered.xml --include tmp/filter.csv -x
python src/merge_xml.py -i tmp/filtered.xml -i prod_make/normal/$OUTXML -o tmp/$MERGEDXML -v 1
python src/sort_xml.py tmp/$MERGEDXML prod_update/normal/$MERGEDXML -v 1
bin/syncupdate.sh
