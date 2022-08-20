python src/csv2xml.py -c src/cfg/y007_accession.yml -i ../data/accessioned/2022/2022.1-2.csv -o prod_update/2022-06-15_2022.xml
mv prod_update/2022-06-15_2022.xml prod_update/normal/2022-06-15_2022.xml
python src/merge_xml.py prod_update/normal/2022-06-05_pe_current_loc2.xml prod_update/normal/2022-06-15_2022.xml prod_update/normal/2022-06-15_merge_2022.xml
bin/pretty prod_update/normal/2022-06-15_merge_2022.xml
