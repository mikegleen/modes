# Set the date to 1935 for some objects. Note that 2022-04-10.sh will correct
# some of these.
#
python src/update_from_csv.py \
 prod_update/normal/2022-04-02_location.xml \
 prod_update/normal/2022-04-07_pottery.xml \
 -c src/cfg/set_circa.yml \
 -m data/csv/2022-04-07_decorative.csv \
 -a
#
# Remove first-published-in name and date from some objects.
#
python src/update_from_csv.py \
 prod_update/normal/2022-04-07_pottery.xml \
 prod_update/normal/2022-04-07_to-day.xml \
 -c src/cfg/set_pub.yml \
 -m data/csv/decorative2.csv \
 -a
