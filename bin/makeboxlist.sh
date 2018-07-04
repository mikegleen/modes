# . activate py6
set -e
pushd ~/pyprj/hrm/modes
python src/list_by_box.py results/jb/xml/f_object_8.xml tmp/jblistbox.csv
python src/list_by_box.py results/sh/xml/sh-06.xml tmp/shlistbox.csv
cat tmp/jblistbox.csv tmp/shlistbox.csv >tmp/bothlistbox.csv
sort -t, -k1,2 tmp/bothlistbox.csv >tmp/sortedlistbox.csv
cut -d , -f 2- tmp/sortedlistbox.csv >tmp/listbox.csv
bin/putbom.sh tmp/listbox.csv tmp/bomlistbox.csv
