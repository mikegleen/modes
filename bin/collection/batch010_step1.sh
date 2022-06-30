python src/web/harvest_scan.py /Users/mlg/Pictures/VueScan/hrmbox  ../harvested
python src/web/harvest_new.py  -d ../collection/aawebimgs -c ../harvested -s tmp/staging -m prod_update/pretty/2022-06-15_merge_2022_pretty.xml
mv tmp/staging ../collection
#
# Images in ../collection are now manually cropped.
#
