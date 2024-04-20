# Updates for 2023-12-11
#
# 1. Move location of two objects.
# 2. Remove all previous locations.
#
set -e
python src/location.py update -i prod_update/normal/2023-12-04a_merged.xml -o prod_update/normal/2023-12-11_location.xml  -l G5 -j JB1070,JB1045 -c -n -a -v 2
#
python src/xml2csv.py prod_update/normal/2023-12-11_location.xml tmp/all.csv --heading
python src/location.py update -i prod_update/normal/2023-12-11_location.xml -o prod_update/normal/2023-12-11a_del_previous.xml --delete_previous -l BARF -a -m tmp/all.csv
bin/syncprod.sh
