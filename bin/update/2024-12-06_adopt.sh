#!/bin/zsh
set -e
python src/update_from_csv.py prod_update/normal/2024-11-15_stormp.xml  prod_delta/normal/2024-12-06_adopt.xml \
    -c src/cfg/oneTime/y010_adopt_a_picture.yml \
    -m 'data/acquisitions/2024-12-06_Acquisitions Evening - Adopt a Picture Feb 2024 Rev 1.xlsx'
python src/update_from_csv.py prod_update/normal/2024-11-15_stormp.xml  prod_update/normal/2024-12-06_adopt.xml \
    -c src/cfg/oneTime/y010_adopt_a_picture.yml \
    -m 'data/acquisitions/2024-12-06_Acquisitions Evening - Adopt a Picture Feb 2024 Rev 1.xlsx' \
    -a
bin/syncdelta.sh
bin/syncupdate.sh
