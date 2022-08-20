#
# Add Exhibition elements to two additional objects.
#
cat >tmp/exhib.csv <<EOF
JB1040
JB1226
EOF
python src/exhibition.py prod_update/normal/2022-08-03_stocktake.xml prod_update/normal/2022-08-12_exhibition.xml \
-e 26 -m tmp/exhib.csv -a
bin/pretty prod_update/normal/2022-08-12_exhibition.xml
