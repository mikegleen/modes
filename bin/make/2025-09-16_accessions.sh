#!/bin/zsh
set -e
INCSV=data/acquisitions/2025-09-16_accessions.xlsx
#
# Input XML file containing the full database in prod_update/normal/
INXML=
#
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('/')[-1].split('.')[0])")
echo SCRIPT: $SCRIPT
# Output XML file containing the new Object records in prod_make/normal/
OUTXML=${SCRIPT}.xml
#
# Output XML file containing the merged and sorted new full database in prod_update/normal
MERGEDXML=${SCRIPT}_merged.xml
cat >tmp/update.yml <<EOF
cmd: global
serial: Accession Number
template_title: Template
template_dir: /Users/mlg/pyprj/hrm/modes/templates/normal
templates:
  Book: book_template.xml
  Ephemera: ephemera_template.xml
  Letter: letter_template.xml
  Cutting: cutting_template.xml
  Artwork: Original_Artwork_template.xml
  Reproduction: reproduction_template.xml
---
column: OE Number
xpath: ./Entry/EntryNumber
---
column: Title
xpath: ./Identification/Title
---
column: Author
xpath: ./Production/Person[Role="author"]/PersonName
---
cmd: column
title: Publisher
xpath: ./Production/Organisation[Role="publisher"]/OrganisationName
if_template: Ephemera | Book
---
cmd: column
title: Publisher 2
column_title: Publisher
xpath: ./Production/Organisation[Role="publication name"]/OrganisationName
if_template: Cutting
---
column: Description
xpath: ./Identification/BriefDescription
---
column: Artist
xpath: ./Production/Person[Role="artist"]/PersonName
person_name:
if_template: Artwork | Reproduction
---
cmd: column
title: Date produced
xpath: ./Production/Date/DateBegin
date:
if_template: Artwork | Reproduction
---
cmd: column
xpath: ./Production/Date/Accuracy
parent_path: ./Production/Date
if_template: Artwork | Reproduction
---
cmd: column
title: Date produced letter
column_title: Date produced
xpath: ./Production/Date
date:
if_template: Letter
---
column: Date published cutting
column_title: Date published
xpath: ./Production/Date
date:
if_template: Cutting
---
column: Date published accuracy cutting
column_title: Date published accuracy
xpath: ./Production/Date/Accuracy
parent_path: ./Production/Date
date:
if_template: Cutting
---
cmd: column
title: Date published
xpath: ./Production/Date[@elementtype="publication date"]/DateBegin
parent_path: ./Production/Date[@elementtype="publication date"]
date:
if_template: Book | Ephemera
---
cmd: column
title: Date published accuracy
xpath: ./Production/Date[@elementtype="publication date"]/Accuracy
parent_path: ./Production/Date[@elementtype="publication date"]
column_title: Accuracy
if_template: Book | Ephemera
---
cmd: column
title: Date published artwork
xpath: ./References/Reference[@elementtype="First Published In"]/Date
column_title: Date published
date:
if_template: Artwork
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
parent_path: ./Acquisition/Organisation[Role="acquired from"]
---
cmd: column
title: Acquisition method
xpath: ./Acquisition/Method
---
cmd: column
title: Size mm HxW
xpath: ./Description/Measurement[Part="image"]/Reading
if_template: Artwork | Reproduction
---
cmd: column
title: Size mm HxW books
column_title: Size mm HxW
xpath: ./Description/Measurement/Reading
if_template: Book | Ephemera
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
column: Sender
xpath: ./Production/Person[Role="sender"]/PersonName
if_template: Letter
---
column: Recipient
xpath: ./Production/Person[Role="recipient"]/PersonName
if_template: Letter
---
column: Sender org
xpath: ./Production/Organisation[Role="sender"]/OrganisationName
if_template: Letter
---
column: Recipient org
xpath: ./Production/Organisation[Role="recipient"]/OrganisationName
if_template: Letter
---
cmd: reproduction
xpath: ./Reproduction/Filename
EOF
python src/csv2xml.py -o prod_make/normal/$OUTXML \
                      -c tmp/update.yml \
                      -i $INCSV \
                      -v 1
bin/syncmake.sh
#
# python src/merge_xml.py -i tmp/filtered.xml -i prod_make/normal/$OUTXML -o tmp/$MERGEDXML -v 1
# python src/sort_xml.py tmp/$MERGEDXML prod_update/normal/$MERGEDXML -v 1
# bin/syncupdate.sh
