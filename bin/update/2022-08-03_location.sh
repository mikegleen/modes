cat >tmp/map.csv <<EOF
Serial,Location,LocationType,Patched,Reason
JB1021,B5,nc,p,Stocktake
LDHRM.2021.23-5,B7,nc,p,Stocktake
JB1114,G7,nc,p,Stocktake
SH50,R3,nc,p,Stocktake
JB1040,Joan Brinsmead Gallery,c,,Humour exhibition
JB1226,Joan Brinsmead Gallery,c,,Humour exhibition
SH58,PE,c
JB437,PE,c
SH78,S22,nc
JB1109,BB3,nc,p
EOF
python src/location.py update -i prod_update/pretty/2022-07_13_locations_pretty.xml -o tmp/2022-08-03_stocktake_pretty.xml --col_loc_type c --col_patch d --col_reason e -m tmp/map.csv -s 1 -v 2 -a
