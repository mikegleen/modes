set -e
python src/location.py update --infile data/test/location/xml/location_$1.xml \
                              --outfile tmp/location_$1.xml \
                              -m data/test/location/csv/location_$1.csv \
                              -r "Good Reason" -c
bin/pretty.sh /Users/mlg/pyprj/hrm/modes/tmp/location_$1.xml
