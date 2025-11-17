#!/bin/zsh
set -e
#
OUTXML=results/xml/test_template.xml
#
cat >tmp/test_template.yml <<EOF
cmd: global
template_title: Template
template_dir: /Users/mlg/pyprj/hrm/modes/templates/normal
templates:
  Book: book_template.xml
  Ephemera: ephemera_template.xml
  Artwork: Original_Artwork_template.xml
  Reproduction: reproduction_template.xml
prefixes:
  JB: 3
  L: 3
  TEST: 2
---
cmd: column
title: OE Number
xpath: ./Entry/EntryNumber
---
column: Title
xpath: ./Identification/Title
---
EOF
cat >tmp/test_template.csv <<EOF
Serial,OE Number,Title,Template
test1,42,Test Template,Artwork
EOF
python src/csv2xml.py -i tmp/test_template.csv -o $OUTXML -c tmp/test_template.yml
