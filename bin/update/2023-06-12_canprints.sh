#!/bin/zsh
INXML=2023-05-21_loc.xml
OUTXML=2023-06-12_canprints.xml
cat >tmp/update.csv <<EOF
Serial,Title,Story,In the Book,Page
2022.11,And turned into a great genie.,Child’s Arabian Nights: The fisherman,Child’s Arabian Nights:,Frontis
2022.12,Up in the air it flew,Child’s Arabian Nights: The magic horse,Child’s Arabian Nights:,p. 20
2022.13,They ordered a great dinner,Child’s Arabian Nights: Aladdin,Child’s Arabian Nights:,p.26
2022.14,"Crying, new lamps for old lamps",Child’s Arabian Nights: Aladdin,Child’s Arabian Nights:,p.31
2022.15,Killed every one of the robbers,Child’s Arabian Nights: Ali Baba,Child’s Arabian Nights:,p.38
2022.16,The sea monster now raised its head,Child’s Arabian Nights: Sinbad,Child’s Arabian Nights:,p.44
2022.17,The bird flew up ever so high,Child’s Arabian Nights: Sinbad,Child’s Arabian Nights:,p.50
2022.18,Drove him about the island,Child’s Arabian Nights: Sinbad,Child’s Arabian Nights:,p.55
2022.19,The slaves bowed down before him,Child’s Arabian Nights: Abu,Child’s Arabian Nights:,p.62
2022.20,Alvaschar had kicked over his basket,Child’s Arabian Nights: Alvaschar,Child’s Arabian Nights:,p.68
2022.21,Gave him a sound boxing on the ear,Child’s Arabian Nights: Shakalik,Child’s Arabian Nights:,p.74
2022.22,The tailor at once carried the poor fellow to the doctor,Child’s Arabian Nights: The fish bone,Child’s Arabian Nights:,p.80
EOF
cat >tmp/update.yml <<EOF
cmd: global
add_mda_code:
---
cmd: constant
xpath: ./Identification/BriefDescription
value:
---
cmd: constant
xpath: ./References
parent_path: .
insert_after: Reproduction
value:
---
cmd: constant
xpath: ./References/Reference
parent_path: ./References
attribute: elementtype
attribute_value: "First Published In"
value:
---
cmd: column
xpath: ./References/Reference/Title
parent_path: ./References/Reference
title: Story
element: Title
---
cmd: column
xpath: ./References/Reference/Page
parent_path: ./References/Reference
---
EOF
python src/update_from_csv.py prod_update/normal/$INXML \
                              prod_update/normal/$OUTXML \
                              -c tmp/update.yml -m tmp/update.csv -r -a -v 2
bin/syncprod.sh
