#
#   Add missing objects to *Shakespeare*
#
cat >tmp/mapfile.csv <<EOF
JB1017-8
JB1023-4
EOF
python src/exhibition.py prod_update/normal/2023-03-15b_dimensions.xml \
                         tmp/2023-03-23_shakespeare.xml \
                         -e 29 -m tmp/mapfile.csv -a
python src/location.py update -i tmp/2023-03-23_shakespeare.xml \
                           -o prod_update/normal/2023-03-23a_shakespeare.xml \
                           -d 29.12.2022 -m tmp/mapfile.csv \
                           -l 'Joan Brinsmead Gallery' \
                           -c -a
#
# Return the Shakespeare objects to the normal locations.
#
python src/xml2csv.py prod_update/normal/2023-03-23a_shakespeare.xml \
                      tmp/shakespeare.csv \
                      -b -c src/cfg/if_exhibition_name.yml \
                      --heading
python src/location.py update -i prod_update/normal/2023-03-23a_shakespeare.xml \
                              -o prod_update/normal/2023-03-23b_shakespeare.xml \
                              -d 19.3.2023 -m tmp/shakespeare.csv -c -a -s 1
