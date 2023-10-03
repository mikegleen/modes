cat >tmp/mapfile.csv <<EOF
JB167
JB168
JB169
JB170
JB171
JB224
JB228
JB230
JB232
JB234
JB235
JB236
JB237
JB239
JB240
JB242
JB243
JB244
JB245
JB626
JB632
JB638
EOF
python src/location.py update -i prod_update/normal/2023-09-19_manual2.xml -o tmp/step1.xml -c -a -d 24.6.2023 -m tmp/mapfile.csv -l 'Joan Brinsmead Gallery'
python src/exhibition.py prod_update/normal/2023-09-19_manual2.xml  prod_update/normal/2023-09-25_perrault.xml -e 32 --col_acc b --col_cat j -s 1
python src/location.py update -i prod_update/normal/2023-09-25_perrault2.xml -o prod_update/normal/2023-09-27_perrault2store.xml -a --col_loc_type c -s 1 -m data/exhibitions/2023-06-24_perrault/perrault_move2store.csv  --date 17.9.2023
python src/location.py update -i prod_update/normal/2023-09-27_perrault2store.xml -o prod_update/normal/2023-09-27a_rabelais2jbg.xml -c -l 'Joan Brinsmead Gallery' -d 23.9.2023 -r 'Illustrating the Grotesque' -m data/exhibitions/rabelais/objects.csv -a -d 23.9.2023
python src/exhibition.py prod_update/pretty/2023-09-27a_rabelais2jbg_pretty.xml prod_update/pretty/2023-09-28_exhibition_pretty.xml  -e 33 -a -m data/exhibitions/rabelais/objects.csv
