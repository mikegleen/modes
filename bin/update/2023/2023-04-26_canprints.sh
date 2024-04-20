#!/bin/zsh
cat >tmp/update.csv <<EOF
Serial,CatalogueNumber,Filename,Title
LDHRM.2022.11,30,LDHRM.2022.11.jpg,And turned into a great genie
LDHRM.2022.12,31,LDHRM.2022.12.jpg,Up in the air it flew
LDHRM.2022.13,32,LDHRM.2022.13.jpg,They ordered a great dinner
LDHRM.2022.14,33,LDHRM.2022.14.jpg,"Crying, “New lamps for old lamps”"
LDHRM.2022.15,34,LDHRM.2022.15.jpg,Killed every one of the robbers
LDHRM.2022.16,35,LDHRM.2022.16.jpg,The sea monster now raised its head
LDHRM.2022.17,36,LDHRM.2022.17.jpg,The bird flew up ever so high
LDHRM.2022.18,37,LDHRM.2022.18.jpg,Drove him about the island
LDHRM.2022.19,38,LDHRM.2022.19.jpg,The slaves bowed down before him
LDHRM.2022.20,39,LDHRM.2022.20.jpg,Alvaschar had kicked over his basket
LDHRM.2022.21,40,LDHRM.2022.21.jpg,Gave him a sound boxing on the ear
LDHRM.2022.22,41,LDHRM.2022.22.jpg,The tailor at once carried the poor fellow to a doctor
EOF
cat >tmp/update.yml <<EOF
cmd: column
xpath: ./Reproduction/Filename
---
cmd: column
xpath: ./Identification/Title
---
EOF
python src/exhibition.py prod_update/normal/2023-04-26_measurement2.xml \
                         prod_update/normal/2023-04-27_canprints.xml \
                         --col_cat B -e 24 -m tmp/update.csv -s 1 -a
python src/update_from_csv.py prod_update/normal/2023-04-27_canprints.xml \
                              prod_update/normal/2023-04-27_canprints2.xml \
                              -c tmp/update.yml -m tmp/update.csv -r -a
bin/syncprod.sh
