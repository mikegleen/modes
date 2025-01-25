#!/bin/zsh
set -e
INCSV=data/acquisitions/2024-10-27_accessions_mlg2.xlsx
#
# Input XML file containing the full database in prod_update/normal/
INXML=2024-12-12_adopt.xml
#
# Output XML file containing the new Object records in prod_make/normal/
OUTXML=2024-10-27_accessions.xml
#
# Output XML file containing the merged and sorted new full database in prod_update/normal
MERGEDXML=2024-10-27_merged_accessions.xml
#
# Directory definitions
#
INPUTDIR=prod_update/normal
NEWOBJDIR=prod_make/normal
OUTPUTDIR=prod_update/normal
#
# config copied from y015_accessions.yml
#
cat >tmp/update.yml <<EOF
# For Accessions 2024-10-27
cmd: global
serial: Accession Number
add_mda_code:
template_title: Template
template_dir: templates/normal
templates:
  Book: book_template.xml
  Cutting: cutting_template.xml
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
column: Publisher
xpath: ./Production/Organisation[Role="publisher"]/OrganisationName
---
column: Description
xpath: ./Identification/BriefDescription
---
column: Date published
parent_path: ./Production/Date[@elementtype="publication date"]
xpath: ./Production/Date[@elementtype="publication date"]/DateBegin
element: DateBegin
---
column: Date published accuracy
parent_path: ./Production/Date[@elementtype="publication date"]
xpath: ./Production/Date[@elementtype="publication date"]/Accuracy
element: Accuracy
---
column: Date acquired
xpath: ./Acquisition/Date
date:
---
column: Acquired from
xpath: ./Acquisition/Person/PersonName
person_name:
---
column: Email
xpath: ./Acquisition/Person/Email
parent_path: ./Acquisition/Person
---
column: Acquisition method
xpath: ./Acquisition/Method
---
column: Size mm HxW
xpath: ./Description/Measurement/Reading
---
column: Medium
xpath: ./Description/Material[Part="medium"]/Keyword
---
column: Location
xpath: ./ObjectLocation[@elementtype="current location"]/Location
xpath2: ./ObjectLocation[@elementtype="normal location"]/Location
---
cmd: constant
xpath: ./ObjectLocation[@elementtype="current location"]/Date/DateBegin
title: 'Date Begin'
value: "27.10.2024"
---
column: Pages
xpath: ./Description/Aspect/Reading
---
column: Condition
xpath: ./Description/Condition/Note
---
column: Notes
xpath: ./Notes
---
EOF
python src/csv2xml.py -o $NEWOBJDIR/$OUTXML \
                      -c tmp/update.yml \
                      -i $INCSV \
                      -v 1
bin/syncmake.sh
python src/merge_xml.py -i $INPUTDIR/$INXML -i $NEWOBJDIR/$OUTXML -o tmp/$MERGEDXML -v 1
python src/sort_xml.py tmp/$MERGEDXML $OUTPUTDIR/$MERGEDXML -v 1
bin/syncupdate.sh
