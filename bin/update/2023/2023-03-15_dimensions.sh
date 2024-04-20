python src/xml2csv.py prod_update/pretty/2023-03-06_edit_pretty.xml tmp/no_dim.csv --include ../collection/etc/batch017update/batch017_no_dimensions.csv
python src/xml2csv.py prod_update/pretty/2023-03-06_edit_pretty.xml tmp/no_dim.csv --include ../collection/etc/batch017update/batch017_no_dimensions.csv -c src/cfg/locations.yml -b
#
# Update the dimensions for the bulk of batch 17
#
python src/web/edit_dimensions.py
python src/update_from_csv.py prod_update/normal/2023-03-06_edit.xml prod_update/normal/2023-03-15_dimensions.xml -c src/cfg/add_dimensions.yml -m ../collection/etc/batch017update/batch017_add_dimensions2.csv -a
bin/syncprod.sh
#
# Update the decorative art (nursery china)
#
python src/update_from_csv.py prod_update/normal/2023-03-15_dimensions.xml prod_update/normal/2023-03-15a_dimensions.xml  -c src/cfg/add_dimensions_decorative_art.yml -m ../collection/etc/batch017update/batch017_add_dimensions_decorative_art.csv -a
bin/syncprod.sh
open prod_update/pretty/2023-03-15a_dimensions_pretty.xml
#
# Update the books
#
python src/update_from_csv.py prod_update/normal/2023-03-15a_dimensions.xml prod_update/normal/2023-03-15b_dimensions.xml -c src/cfg/add_dimensions_decorative_art.yml -m /Users/mlg/pyprj/hrm/collection/etc/batch017update/batch017_add_dimensions_book.csv -a
bin/syncprod.sh
