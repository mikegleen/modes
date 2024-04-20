python src/update_from_csv.py \
	prod_update/normal/2023-03-25_shakespeare.xml \
	prod_update/normal/2023-03-30_batch019.xml \
	-c src/cfg/website_update.yml \
	-m ../collection/etc/batch019/batch019_fix.csv -r -a

