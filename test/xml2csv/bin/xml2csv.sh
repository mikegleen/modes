tpath=test/xml2csv
tst=$1
shift
python src/xml2csv.py $tpath/xml/$tst.xml $tpath/results/$tst.csv -c $tpath/yml/$tst.yml $*
# diff -q $tpath/baseline/$tst.csv $tpath/results/$tst.csv
