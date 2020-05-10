# Call this script with the name of the test followed by any parameters to pass to python.
#
app=`basename $0|cut -d. -f1`
tpath=test/$app
tst=$1
shift
python src/$app.py $tpath/xml/$tst.xml $tpath/results/$tst.xml -c $tpath/yml/$tst.yml -m  $tpath/csv/$tst.csv $*
diff -q $tpath/baseline/$tst.xml $tpath/results/$tst.xml &>/dev/null
if [ $? ]
then
diff -q $tpath/baseline/$tst.xml $tpath/results/$tst.xml
fi
