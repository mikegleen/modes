#!/bin/zsh
set -e
INCSV=../collection/etc/batch026/accession_batch026.xlsx
#
# Input XML file containing the full database in prod_update/normal/
INXML=2024-10-25_fix_sizes.xml
#
# Output XML file containing the new Object records in prod_make/normal/
OUTXML=2024-10-25_batch026_accessions.xml
#
# Output XML file containing the merged and sorted new full database in prod_update/normal
MERGEDXML=2024-10-25_merged_batch026_accessions.xml
cat >tmp/update.yml <<EOF
cmd: global
template_title: Template
template_dir: /Users/mlg/pyprj/hrm/modes/templates/normal
templates:
  Book: book_template.xml
  ephemera: ephemera_template.xml
  letter: letter_template.xml
  Artwork: Original_Artwork_template.xml
  Reproduction: reproduction_template.xml
---
column: Title
xpath: ./Identification/Title
---
column: Description
xpath: ./Identification/BriefDescription
---
cmd: column
title: Date
xpath: ./Production/Date[@elementtype="publication date"]/DateBegin
parent_path: ./Production/Date[@elementtype="publication date"]
date:
if_other_column: Template
if_other_column_value: ephemera
---
cmd: column
title: Letter Date
column_title: Date
xpath: ./Production/Date/DateBegin
parent_path: ./Production/Date
date:
if_other_column: Template
if_other_column_value: letter
---
cmd: column
title: Size
xpath: ./Description/Measurement/Reading
if_other_column: Template
if_other_column_value: ephemera
---
cmd: column
title: Location
xpath: ./ObjectLocation[@elementtype="current location"]/Location
xpath2: ./ObjectLocation[@elementtype="normal location"]/Location
---
cmd: constant
title: Location datebegin
xpath: ./ObjectLocation[@elementtype="current location"]/Date/DateBegin
value: 13.9.2023
---
cmd: column
title: Pages
xpath: ./Description/Aspect[Keyword="pages"]/Reading
---
EOF
python src/csv2xml.py -o prod_make/normal/$OUTXML \
                      -c tmp/update.yml \
                      -i $INCSV \
                      -v 1
bin/syncmake.sh
python src/merge_xml.py -i prod_update/normal/$INXML -i prod_make/normal/$OUTXML -o tmp/$MERGEDXML -v 1
python src/sort_xml.py tmp/$MERGEDXML prod_update/normal/$MERGEDXML -v 1
bin/syncupdate.sh
