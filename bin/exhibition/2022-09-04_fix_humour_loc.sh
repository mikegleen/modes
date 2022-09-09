cat >tmp/map.csv <<EOF
JB301
JB302
JB1213.018
JB1213.020A
JB1213.23
JB1213.025A
JB1031
JB1045
JB1042
JB1044
EOF
python src/location.py update -i prod_update/pretty/2022-08-25_entry2_pretty.xml -o prod_update/pretty/2022-09-04_fix_humour_pretty.xml -a -c -m tmp/map.csv -l 'Joan Brinsmead Gallery' -d 10.6.2022 -r 'Humour exhibition' -f
