tpath=data/test/xml2csv
tst=$1
shift
python src/xml2csv.py $tpath/xml/$tst.xml tmp/update_test.xml -c $tpath/yml/$tst.yml $*
echo ----Results:----
cat tmp/update_test.xml