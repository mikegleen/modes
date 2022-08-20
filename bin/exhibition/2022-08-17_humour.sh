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
python src/exhibition.py prod_update/pretty/2022-08-15_edit_pretty.xml prod_update/pretty/2022-08-17_humour_pretty.xml -e 26 -a -m tmp/map.csv -v 2
bin/normal prod_update/pretty/2022-08-17_humour_pretty.xml
