python src/exhibition.py prod_update/pretty/2023-09-30_SH100_pretty.xml prod_update/pretty/2023-09-30a_SH100_pretty.xml -a -j 'SH100A,SH100B' -e 28
python src/location.py update -i prod_update/pretty/2023-09-30a_SH100_pretty.xml -o prod_update/pretty/2023-09-30b_SH100_pretty.xml -n -l S21 -j 'SH100A,SH100B' -a
python src/location.py update -i prod_update/pretty/2023-09-30b_SH100_pretty.xml -o prod_update/pretty/2023-09-30c_SH100_pretty.xml -c -l 'Somerset House' -d 21.10.2021 -j 'SH100A,SH100B' -a
python src/location.py update -i prod_update/pretty/2023-09-30c_SH100_pretty.xml -o prod_update/pretty/2023-09-30d_SH100_pretty.xml -c -l S21 -d 3.4.2022 -j 'SH100A,SH100B' -a
