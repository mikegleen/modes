#!/bin/zsh
#
#   Apply two changes for the adopt-a-picture objects:
#   1. Add the <Aspect> group
#   2. Update the locations for the pictures taken out of frames.
#
set -e
#
#   Create delta XML file
#
python src/update_from_csv.py prod_update/normal/2024-11-15_stormp.xml  tmp/normal/2024-12-06_adopt.xml \
    -c src/cfg/y010_adopt_a_picture.yml \
    -m 'data/acquisitions/2024-12-06_Acquisitions Evening - Adopt a Picture Feb 2024 Rev 1.xlsx'
python src/location.py update -i tmp/normal/2024-12-06_adopt.xml -o prod_delta/normal/2024-12-12_adopt.xml \
    --col_acc Serial --col_loc Location -c -n --reason "Removed picture from frame" \
    -m data/acquisitions/2024-12-07_Adopt_a_Picture_Locations.xlsx
bin/syncdelta.sh
#
#   Create full XML file
#
    python src/update_from_csv.py prod_update/normal/2024-11-15_stormp.xml  tmp/normal/2024-12-06_adopt.xml \
    -c src/cfg/y010_adopt_a_picture.yml \
    -m 'data/acquisitions/2024-12-06_Acquisitions Evening - Adopt a Picture Feb 2024 Rev 1.xlsx' \
    -a
python src/location.py update -i tmp/normal/2024-12-06_adopt.xml -o prod_update/normal/2024-12-12_adopt.xml \
    --col_acc Serial --col_loc Location -c -n --reason "Removed picture from frame" \
    -m data/acquisitions/2024-12-07_Adopt_a_Picture_Locations.xlsx \
    -a
bin/syncupdate.sh
#
#   Extract the original objects corresponding to the updated ones and insert line feeds so that we can do a diff
#   with the new delta pretty file.
#
python src/xmldiff.py prod_update/normal/2024-11-15_stormp.xml prod_update/normal/2024-12-12_adopt.xml --outorig tmp/before.xml
python src/pretty_xml.py tmp/before.xml -o tmp/before_pretty.xml
