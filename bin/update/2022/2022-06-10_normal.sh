#
echo Update the normal location for affected Stories pictures.
#
python src/location.py update -i prod_update/normal/2022-05-02_merge.xml -o prod_update/normal/2022-06-04_stories_new_normal.xml --col_loc 3 -m data/object_movement/2022-06-04/stories17may22.csv -n -s 4 -v 2 --all
#
echo Move the Stories pictures to the store
#
python src/location.py update -i prod_update/normal/2022-06-04_stories_new_normal.xml -o prod_update/normal/2022-06-04_stories_current.xml --col_loc 7 -m results/csv/exhibitions/children_final_new_locs.csv  -c -s 1 -v 2 --col_acc 1 -a -r 'Children Stories back to store'
#
echo Move the Humour pictures to JBG
#
python src/location.py update -i prod_update/normal/2022-06-04_stories_current.xml -o prod_update/normal/2022-06-04_humour_current.xml -m results/csv/exhibitions/humour_final.csv -c -s 1 -v 2 --col_acc 1 -a -l "Joan Brinsmead Gallery" -r 'Humour exhibition'
#
echo Add the <Exhibition> record for Humour.
#
python src/exhibition.py prod_update/normal/2022-06-04_humour_current.xml prod_update/normal/2022-06-04_humour_exhibition.xml -m results/csv/exhibitions/humour_final_with_serial.csv --col_acc 1 -e 26 --col_cat 0 -a -s 1
#
echo Update the normal location for pictures moved from the permanent exhibition.
#
python src/location.py update -i prod_update/normal/2022-06-04_humour_exhibition.xml -o prod_update/normal/2022-06-05_pe_normal_loc.xml -m results/csv/2022-05-09_from_pe.csv --col_loc  2 -n --heading 'Return to:' -r "PE Changeover" -a -v 2
#
echo Move the pictures from PE to store except the ones still in the Humour exhibition.
#
python src/location.py update -i prod_update/normal/2022-06-05_pe_normal_loc.xml -o prod_update/normal/2022-06-05_pe_current_loc.xml -m results/csv/2022-05-09_from_pe_to_store.csv --col_loc  2 -c --heading 'Return to:' -r "PE Changeover" -a -v 2
#
echo Move pictures from the store to PE
#
python src/location.py update -i prod_update/normal/2022-06-05_pe_current_loc.xml -o prod_update/normal/2022-06-05_pe_current_loc2.xml -m results/csv/2022-05-09_to_pe.csv -a -l PE  -c -v 2 -r "PE Changeover"
#
echo Make a human-readable version
#
bin/pretty prod_update/normal/2022-06-05_pe_current_loc2.xml
