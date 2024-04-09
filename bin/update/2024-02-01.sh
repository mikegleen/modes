# Updates for 2024-02-01
#
# Apply changes skipping the removal of previous locations.
#
# 1. Move location of two objects.
# 2. Remove all previous locations.
#
set -e
python src/location.py update -i prod_update/normal/2023-12-04a_merged.xml -o prod_update/normal/2024-02-01_location.xml  -l G5 -j JB1070,JB1045 -c -n -a -v 2
#
cat >tmp/grotesque.csv <<EOF
Serial,Normal Location,Current Location
JB083,G1,Joan Brinsmead Gallery
JB084,G1,Joan Brinsmead Gallery
JB101,G1,Joan Brinsmead Gallery
JB102,G1,Joan Brinsmead Gallery
JB104,G1,Joan Brinsmead Gallery
JB111,G1,Joan Brinsmead Gallery
JB114,G1,Joan Brinsmead Gallery
JB115,S16,Joan Brinsmead Gallery
JB1063,B3,Joan Brinsmead Gallery
EOF
python src/location.py update -i prod_update/normal/2024-02-01_location.xml -o prod_update/normal/2024-02-01a_grotesque2store.xml -q -c -m tmp/grotesque.csv -a
#
python src/exhibition.py prod_update/normal/2024-02-01a_grotesque2store.xml prod_update/normal/2024-02-01b_mottisfont.xml -a --col_acc e -e 34 -s 1 -m results/csv/exhibitions/2024-01-20_mottisfont.csv
#
python src/location.py update -m results/csv/exhibitions/2024-01-20_mottisfont.csv  --col_acc e -i prod_update/normal/2024-02-01b_mottisfont.xml -c -l 'Mottisfont Abbey' -o prod_update/normal/2024-02-01c_mottisfontloc.xml -s 1  -a
#
python src/location.py update -i prod_update/normal/2024-02-01c_mottisfontloc.xml -o prod_update/normal/2024-02-01d_G1_to_G2.xml -l G2 -j 'JB273&306&308&310&302&266&295&297&303&296&307&300&267&268&294&275&311&256' -a -c -n
#
bin/syncprod.sh
